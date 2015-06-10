#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test pymlac opcode DIRECTLY.

Put opcodes into memory along with required memory values.
Put L and AC values into registers.
Execute opcode, test result.

We DON'T try to load from papertape, use core files, etc.
"""


import unittest

import MainCPU
import Memory
import Trace

class TestPymlac(unittest.TestCase):

    def test_LAW(self):
        Trace.init('test_LAW.trace')
        Trace.settrace(True)
        Memory.init()

        # test "LAW 0"
        Memory.memory[0100] = 004000    # LAW 0
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LAW 0" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LAW 0" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"LAW 0" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"LAW 0" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        Memory.memory[0100] = 004000    # LAW 0
        MainCPU.AC = 012345
        MainCPU.L = 0
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LAW 0" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LAW 0" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"LAW 0" modified L to %01o, should be 0' % MainCPU.L
        self.assertTrue(MainCPU.L == 0, msg)
        msg = '"LAW 0" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        # test "LAW 0377"
        Memory.memory[0100] = 004377    # LAW 0377
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LAW 0377" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LAW 0377" left AC containing %06o, should be 0377' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0377, msg)
        msg = '"LAW 0377" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"LAW 0377" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        Memory.memory[0100] = 004377    # LAW 0377
        MainCPU.AC = 012345
        MainCPU.L = 0
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LAW 0377" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LAW 0377" left AC containing %06o, should be 0377' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0377, msg)
        msg = '"LAW 0377" modified L to %01o, should be 0' % MainCPU.L
        self.assertTrue(MainCPU.L == 0, msg)
        msg = '"LAW 0377" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

    def test_LWC(self):
        Trace.init('test_LWC.trace')
        Trace.settrace(True)
        Memory.init()

        # test "LWC 0"
        Memory.memory[0100] = 0104000    # LWC 0
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LWC 0" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LWC 0" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"LWC 0" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"LWC 0" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        Memory.memory[0100] = 0104000    # LWC 0
        MainCPU.AC = 012345
        MainCPU.L = 0
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LWC 0" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LWC 0" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"LWC 0" modified L to %01o, should be 0' % MainCPU.L
        self.assertTrue(MainCPU.L == 0, msg)
        msg = '"LWC 0" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        # test "LWC 1"
        Memory.memory[0100] = 0104001    # LWC 1
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LWC 1" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LWC 1" left AC containing %06o, should be 0177776' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177776, msg)
        msg = '"LWC 1" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"LWC 1" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        Memory.memory[0100] = 0104001    # LWC 1
        MainCPU.AC = 012345
        MainCPU.L = 0
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"LWC 1" used %d cycles, should be 1' % cycles
        self.assertTrue(cycles == 1, msg)
        msg = '"LWC 1" left AC containing %06o, should be 0177776' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177776, msg)
        msg = '"LWC 1" modified L to %01o, should be 0' % MainCPU.L
        self.assertTrue(MainCPU.L == 0, msg)
        msg = '"LWC 1" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

    def test_JMP(self):
        Trace.init('test_JMP.trace')
        Trace.settrace(True)
        Memory.init()

        # test "JMP 0110"
        Memory.memory[0100] = 0010110    # JMP 0110
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"JMP 0110" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"JMP 0110" left AC containing %06o, should be 012345' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 012345, msg)
        msg = '"JMP 0110" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"JMP 0110" modified PC to %06o, should be 0110' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0110, msg)



################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(TestPymlac, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

