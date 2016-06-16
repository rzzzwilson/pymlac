#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac Memory object DIRECTLY.

Usage: test_Memory.py [<options>]

where <options> is one or more of
          -h    prints this help and stops
"""

import os
import unittest

from Globals import *
import Memory

import log
log = log.Log('test_CPU.log', log.Log.DEBUG)


def save_memory():
    """Save memory to a returned array."""

    pass


class TestMemory(unittest.TestCase):

    def test_simple(self):
        """Check Memory instantiation."""

        memory = Memory.Memory()
        msg = 'Expected Memory() instance, got %s' % str(memory)
        self.assertTrue(memory is not None, msg)

    def test_PTR(self):
        """Check Memory instantiation using PTR ROM."""

        memory = Memory.Memory(boot_rom=ROM_PTR)
        msg = 'Expected Memory(boot_rom=ROM_PTR) instance, got %s' % str(memory)
        self.assertTrue(memory is not None, msg)

    def test_TTY(self):
        """Check Memory instantiation using TTY ROM."""

        memory = Memory.Memory(boot_rom=ROM_TTY)
        msg = 'Expected Memory(boot_rom=ROM_TTY) instance, got %s' % str(memory)
        self.assertTrue(memory is not None, msg)

    def test_NONE(self):
        """Check Memory instantiation using NONE ROM."""

        memory = Memory.Memory(boot_rom=ROM_NONE)
        msg = 'Expected Memory(boot_rom=ROM_NONE) instance, got %s' % str(memory)
        self.assertTrue(memory is not None, msg)

    def test_fetch_put_direct(self):
        """Check Memory put/fetch."""

        memory = Memory.Memory(boot_rom=ROM_NONE)

        # check various locations
        last_value = None
        for address in [0, 0o40] + range(0o100, MEMORY_SIZE, 0o100):
            for value in range(0, WORDMASK, 0o10):
                memory.put(value=value, address=address, indirect=False)
                fetch_value = memory.fetch(address=address, indirect=False)
                msg = 'Fetch from %07o got %07o, expected %07o' % (address, fetch_value, value)
                self.assertTrue(value == fetch_value, msg)
                last_value = fetch_value

        # now check again that last value still in all those locations
        for address in [0, 0o40] + range(0o100, MEMORY_SIZE, 0o100):
            fetch_value = memory.fetch(address=address, indirect=False)
            msg = 'Fetch from %07o got %07o, expected %07o' % (address, fetch_value, last_value)
            self.assertTrue(last_value == fetch_value, msg)

    def test_fetch_put_indirect(self):
        """Check Memory put/fetch indirect."""

        memory = Memory.Memory(boot_rom=ROM_NONE)

        expected = 0o125252

        # address 010 is target of all indirect fetches
        memory.put(value=expected, address=0o10, indirect=False)

        # fill all test addresses with pointer to address 010
        for address in range(0, MEMORY_SIZE, 0o100):
            memory.put(value=0o10, address=address, indirect=False)

        # now check that fetch through all those addresses gets contents of 010
        for address in range(0, MEMORY_SIZE, 0o100):
            fetch_value = memory.fetch(address=address, indirect=True)
            msg = 'Fetch of 010 through %07o got %07o, expected %07o' % (address, fetch_value, expected)
            self.assertTrue(expected == fetch_value, msg)

    def test_fetch_put_autoinc_direct(self):
        """Check Memory put/fetch autoinc direct."""

        memory = Memory.Memory(boot_rom=ROM_NONE)

        expected = 0o052525

        # fill all test addresses with expected value - 1
        for address in range(0o10, 0o17):
            memory.put(value=expected-1, address=address, indirect=False)

        # now check that fetch through all those addresses increments the location
        for address in range(0o10, 0o17):
            fetch_value = memory.fetch(address=address, indirect=True)

            # check that autoinc memory has incremented
            fetch_value = memory.fetch(address=address, indirect=False)
            msg = 'Location %07o should be %07o, actually %07o' % (address, expected, fetch_value)
            self.assertTrue(expected == fetch_value, msg)

    def test_fetch_put_autoinc_indirect(self):
        """Check Memory put/fetch autoinc indirect."""

        memory = Memory.Memory(boot_rom=ROM_NONE)

        expected = 0o052525

        # address 0100 is target of all indirect fetches
        memory.put(value=expected, address=0o100, indirect=False)

        # fill all test addresses with pointer to address 0077
        for address in range(0o10, 0o17):
            memory.put(value=0o077, address=address, indirect=False)

        # now check that fetch through all those addresses gets contents of 0100
        for address in range(0o10, 0o17):
            fetch_value = memory.fetch(address=address, indirect=True)
            msg = 'Fetch of 0100 through %07o got %07o, expected %07o' % (address, fetch_value, expected)
            self.assertTrue(expected == fetch_value, msg)

            # check that autoinc memory has incremented
            fetch_value = memory.fetch(address=address, indirect=False)
            msg = 'Location %07o should be %07o, actually %07o' % (address, 0o100, fetch_value)
            self.assertTrue(0o100 == fetch_value, msg)

    def test_fetch_put_all_values(self):
        """Check Memory put/fetch for all word values."""

        memory = Memory.Memory(boot_rom=ROM_NONE)

        # now check that put/fetch through all test addresses for all values
        for address in range(0, 0o10, 0o10):
            for value in range(WORDMASK):
                memory.put(value=value, address=address, indirect=False)
                fetch_value = memory.fetch(address=address, indirect=False)
                msg = 'Fetch of location %07o got %07o, expected %07o' % (address, fetch_value, value)
                self.assertTrue(value == fetch_value, msg)


################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(TestMemory,'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)
