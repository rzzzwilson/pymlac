#!/usr/bin/env python

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
                 ('A', 0o100, {'A': 1}, 1, None, False),
                 ('.', 0o100, {}, 0o100, None, False),
                 ('B', 0o100, {}, None, 'B', True),
                 ('A+1', 0100, {'A': 1}, 2, None, False),
                 ('A+B', 0, {'A': 1, 'B': 2}, 3, None, False),
                 ('A + B', 0, {'A': 1, 'B': 2}, 3, None, False),
                 ('A / B', 0, {'A': 4, 'B': 2}, 2, None, False),
                 ('. + 0o100', 0o100, {}, 0o200, None, False),
                )

        # now run them
        for (test, dot, symtable, expected, undefined, raises) in tests:
            with open('test_list_file', 'wb') as pyasm.ListFileHandle:
                pyasm.Undefined = None
                pyasm.SymTable = symtable
                pyasm.Dot = dot
                if raises:
                    result = None
                    with self.assertRaises(NameError):
                        result = pyasm.eval_expr(test)
                else:
                    result = pyasm.eval_expr(test)
                msg = ("Expected eval_expression('%s', '%s') to return '%s', got '%s'"
                       % (test, str(dot), str(expected), str(result)))
                self.assertEqual(result, expected, msg)
                msg = ("Expected eval_expression('%s', '%s') to set Undefined to '%s', got '%s'"
                       % (test, str(dot), str(undefined), str(pyasm.Undefined)))
                self.assertEqual(undefined, pyasm.Undefined, msg)

    def test_split_fields(self):
        """Run lots of tests on split_fields()."""

        # define tests: (test, expected)
        tests = (('label opcode value ;comment', ('LABEL', 'OPCODE', False, 'VALUE')),
                 ('',                            (None, None, False, None)),
                 (';comment',                    (None, None, False, None)),
                 ('; comment',                   (None, None, False, None)),
                 (' ; comment',                  (None, None, False, None)),
                 ('\t; comment',                 (None, None, False, None)),
                 ('label',                       ('LABEL', None, False, None)),
                 (' opcode',                     (None, 'OPCODE', False, None)),
                 ('\topcode',                    (None, 'OPCODE', False, None)),
                 ('label opcode',                ('LABEL', 'OPCODE', False, None)),
                 ('label\topcode',               ('LABEL', 'OPCODE', False, None)),
                 ('label opcode value',          ('LABEL', 'OPCODE', False, 'VALUE')),
                 ('label\topcode value',         ('LABEL', 'OPCODE', False, 'VALUE')),
                 ('label\topcode\tvalue',        ('LABEL', 'OPCODE', False, 'VALUE')),
                 ('label opcode a+b',            ('LABEL', 'OPCODE', False, 'A+B')),
                 ('label opcode a + b',          ('LABEL', 'OPCODE', False, 'A + B')),
                 ('      opcode a + b',          (None, 'OPCODE', False, 'A + B')),
                 ('      opcode a + b ;comment', (None, 'OPCODE', False, 'A + B')),
                 ('      opcode',                (None, 'OPCODE', False, None)),
                )

        # now run them
        pyasm.CurrentLineNumber = 1
        for (test, expected) in tests:
            pyasm.CurrentLine = test
            result = pyasm.split_fields(test)
            msg = ("Expected split_fields('%s') to return '%s', got '%s'"
                   % (test, str(expected), str(result)))
            self.assertEqual(result, expected, msg)

    def test_define_label(self):
        """Run lots of tests on define_label().

        Note that we CAN'T test defining a label twice as define_line() will
        call sys.exit().
        """

        # define tests: (label, address, lnum, expected_symtab, expected_symtabline
        tests = (
                 ('A', 1, 2, {'A': 1}, {'A': 2}),
                 ('B', 0o100, 5, {'B': 0o100}, {'B': 5}),
                )

        # now run them
        for (label, address, lnum, exp_symtab, exp_symtabline) in tests:
            pyasm.SymTable = {}
            pyasm.SymTableLine = {}
            pyasm.define_label(label, address, lnum)
            msg = ("Expected define_label('%s', %d, %d) to set SymTable '%s', got '%s'"
                   % (label, address, lnum, str(exp_symtab), str(pyasm.SymTable)))
            self.assertEqual(exp_symtab, pyasm.SymTable, msg)
            msg = ("Expected define_label('%s', %d, %d) to set SymTableLine '%s', got '%s'"
                   % (label, address, lnum, str(exp_symtabline), str(pyasm.SymTableLine)))
            self.assertEqual(exp_symtabline, pyasm.SymTableLine, msg)

################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(TestPyasm, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
