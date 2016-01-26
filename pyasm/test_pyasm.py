#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pyasm functions.

Usage: test_pyasm.py [<options>]

where <options> is one or more of
          -h    prints this help and stops
"""

import os
import pyasm
import unittest


class TestPyasm(unittest.TestCase):

    def test_eval_expression(self):
        """Run tests on eval(expression).

        eval_expression(expr, dot) with SymTable global
        """

        # define tests: (test, dot, symtable, expected, undefined, raises)
        tests = (
                 ('a', 0100, {'A': 1}, 1, None, False),
                 ('.', 0100, {}, 0100, None, False),
                 ('b', 0100, {}, None, 'B', True),
                 ('a+1', 0100, {'A': 1}, 2, None, False),
                 ('a+b', 0, {'A': 1, 'B': 2}, 3, None, False),
                 ('a + b', 0, {'A': 1, 'B': 2}, 3, None, False),
                 ('a / b', 0, {'A': 4, 'B': 2}, 2, None, False),
                 ('. + 0100', 0100, {}, 0200, None, False),
                )

        # now run them
        for (test, dot, symtable, expected, undefined, raises) in tests:
            pyasm.Undefined = None
            pyasm.SymTable = symtable
            if raises:
                result = None
                with self.assertRaises(NameError):
                    result = pyasm.eval_expression(test, dot)
            else:
                result = pyasm.eval_expression(test, dot)
            msg = ("Expected eval_expression('%s', '%s') to return '%s', got '%s'"
                   % (test, str(dot), str(expected), str(result)))
            self.assertEqual(result, expected, msg)
            msg = ("Expected eval_expression('%s', '%s') to set Undefined to '%s', got '%s'"
                   % (test, str(dot), str(undefined), str(pyasm.Undefined)))
            self.assertEqual(undefined, pyasm.Undefined, msg)

    def test_split_fields(self):
        """Run lots of tests on split_fields()."""

        # define tests: (test, expected)
        tests = (('label opcode value ;comment', ('LABEL', 'OPCODE', 'value')),
                 ('',                            (None, None, None)),
                 (';comment',                    (None, None, None)),
                 ('; comment',                   (None, None, None)),
                 (' ; comment',                  (None, None, None)),
                 ('\t; comment',                 (None, None, None)),
                 ('label',                       ('LABEL', None, None)),
                 (' opcode',                     (None, 'OPCODE', None)),
                 ('\topcode',                    (None, 'OPCODE', None)),
                 ('label opcode',                ('LABEL', 'OPCODE', None)),
                 ('label\topcode',               ('LABEL', 'OPCODE', None)),
                 ('label opcode value',          ('LABEL', 'OPCODE', 'value')),
                 ('label\topcode value',         ('LABEL', 'OPCODE', 'value')),
                 ('label\topcode\tvalue',        ('LABEL', 'OPCODE', 'value')),
                 ('label opcode a+b',            ('LABEL', 'OPCODE', 'a+b')),
                 ('label opcode a + b',          ('LABEL', 'OPCODE', 'a + b')),
                 ('      opcode a + b',          (None, 'OPCODE', 'a + b')),
                 ('      opcode a + b ;comment', (None, 'OPCODE', 'a + b')),
                 ('      opcode',                (None, 'OPCODE', None)),
                )

        # now run them
        for (test, expected) in tests:
            result = pyasm.split_fields(test)
            msg = ("Expected split_fields('%s') to return '%s', got '%s'"
                   % (test, str(expected), str(result)))
            self.assertEqual(result, expected, msg)

################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(TestPyasm, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
