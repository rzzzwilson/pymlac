#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test pymlac CPU opcodes DIRECTLY.

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

        # test "JMP 0100"
        Memory.memory[0100] = 0010100    # JMP 0100
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"JMP 0100" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"JMP 0100" left AC containing %06o, should be 012345' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 012345, msg)
        msg = '"JMP 0100" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"JMP 0100" modified PC to %06o, should be 0100' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0100, msg)

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

        # test "JMP *0110"
        Memory.memory[0100] = 0110110    # JMP *0110
        Memory.memory[0110] = 0120       # where next PC should be
        MainCPU.init()
        MainCPU.AC = 012345
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"JMP *0110" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"JMP *0110" left AC containing %06o, should be 012345' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 012345, msg)
        msg = '"JMP *0110" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"JMP *0110" modified PC to %06o, should be 0120' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0120, msg)

    def test_DAC(self):
        Trace.init('test_DAC.trace')
        Trace.settrace(True)
        Memory.init()

        # test "DAC 0101"
        Memory.memory[0100] = 0020101    # DAC 0101
        Memory.memory[0101] = 0          # value we are storing over
        MainCPU.init()
        MainCPU.AC = 1
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"DAC 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"DAC 0101" left AC containing %06o, should be 1' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 1, msg)
        msg = '"DAC 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"DAC 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"DAC 0101" modified memory[0101] to %06o, should be 1' % Memory.memory[0101]
        self.assertTrue(Memory.memory[0101] == 1, msg)

        # test "DAC *0101"
        Memory.memory[0100] = 0120101    # DAC *0101
        Memory.memory[0101] = 0102       # address of cell we are storing into
        Memory.memory[0102] = 0
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"DAC *0101" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"DAC *0101" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"DAC *0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"DAC *0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"DAC *0101" modified memory[0102] to %06o, should be 0177777' % Memory.memory[0102]
        self.assertTrue(Memory.memory[0102] == 0177777, msg)

    def test_XAM(self):
        Trace.init('test_XAM.trace')
        Trace.settrace(True)
        Memory.init()

        # test "XAM 0101"
        Memory.memory[0100] = 0024101    # XAM 0101
        Memory.memory[0101] = 0          # value we are exchanging
        MainCPU.init()
        MainCPU.AC = 2
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"XAM 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"XAM 0101" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"XAM 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"XAM 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"XAM 0101" modified memory[0101] to %06o, should be 2' % Memory.memory[0101]
        self.assertTrue(Memory.memory[0101] == 2, msg)

        # test "XAM *0101"
        Memory.memory[0100] = 0124101    # XAM *0101
        Memory.memory[0101] = 0102       # address of cell we are storing into
        Memory.memory[0102] = 0
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"XAM *0101" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"XAM *0101" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"XAM *0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"XAM *0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"XAM *0101" modified memory[0102] to %06o, should be 0177777' % Memory.memory[0102]
        self.assertTrue(Memory.memory[0102] == 0177777, msg)

    def test_ISZ(self):
        Trace.init('test_ISZ.trace')
        Trace.settrace(True)
        Memory.init()

        # test "ISZ 0101"
        Memory.memory[0100] = 0030101    # ISZ 0101
        Memory.memory[0101] = 0          # value we are incrementing/testing
        MainCPU.init()
        MainCPU.AC = 2
        msg = 'Before, AC contains %06o, should be 2' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 2, msg)
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ISZ 0101" left AC containing %06o, should be 2' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 2, msg)
        msg = '"ISZ 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"ISZ 0101" modified memory[0101] to %06o, should be 1' % Memory.memory[0101]
        self.assertTrue(Memory.memory[0101] == 1, msg)

        # test "ISZ *0101"
        Memory.memory[0100] = 0130101    # ISZ *0101
        Memory.memory[0101] = 0102       # address of cell we are storing into
        Memory.memory[0102] = 0
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ *0101" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"ISZ *0101" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"ISZ *0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ *0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"ISZ *0101" modified memory[0102] to %06o, should be 1' % Memory.memory[0102]
        self.assertTrue(Memory.memory[0102] == 1, msg)

        # test "ISZ 0101"
        Memory.memory[0100] = 0030101    # ISZ 0101
        Memory.memory[0101] = 0177777    # value we are incrementing/testing
        MainCPU.init()
        MainCPU.AC = 2
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ISZ 0101" left AC containing %06o, should be 2' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 2, msg)
        msg = '"ISZ 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ 0101" modified PC to %06o, should be 0102' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0102, msg)
        msg = '"ISZ 0101" modified memory[0101] to %06o, should be 0' % Memory.memory[0101]
        self.assertTrue(Memory.memory[0101] == 0, msg)

        # test "ISZ *0101"
        Memory.memory[0100] = 0130101    # ISZ *0101
        Memory.memory[0101] = 0102       # address of cell we are storing into
        Memory.memory[0102] = 0177777
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ *0101" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"ISZ *0101" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"ISZ *0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ *0101" modified PC to %06o, should be 0102' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0102, msg)
        msg = '"ISZ *0101" modified memory[0102] to %06o, should be 0' % Memory.memory[0102]
        self.assertTrue(Memory.memory[0102] == 0, msg)

        # test "ISZ 010"        check auto-increment locations
        Memory.memory[0100] = 0030010    # ISZ 010
        Memory.memory[010] = 0           # value we are incrementing/testing
        MainCPU.init()
        MainCPU.AC = 2
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ 010" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ISZ 010" left AC containing %06o, should be 2' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 2, msg)
        msg = '"ISZ 010" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ 010" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"ISZ 010" modified memory[010] to %06o, should be 1' % Memory.memory[010]
        self.assertTrue(Memory.memory[010] == 1, msg)

        # test "ISZ *010"
        Memory.memory[0100] = 0130010    # ISZ *010
        Memory.memory[010] = 0102        # address of cell we are storing into
        Memory.memory[0102] = 0
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ISZ *010" used %d cycles, should be 3' % cycles
        self.assertTrue(cycles == 3, msg)
        msg = '"ISZ *010" left AC containing %06o, should be 0177777' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0177777, msg)
        msg = '"ISZ *010" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ISZ *010" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)
        msg = '"ISZ *010" modified memory[010] to %06o, should be 0103' % Memory.memory[010]
        self.assertTrue(Memory.memory[010] == 0103, msg)
        msg = '"ISZ *010" modified memory[0102] to %06o, should be 1' % Memory.memory[0102]
        self.assertTrue(Memory.memory[0102] == 1, msg)

    def test_ADD(self):
        Trace.init('test_ADD.trace')
        Trace.settrace(True)
        Memory.init()

        # test "ADD 0101"
        Memory.memory[0100] = 0064101    # ADD 0101
        Memory.memory[0101] = 0          # value we are adding to PC
        MainCPU.init()
        MainCPU.AC = 0
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ADD 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ADD 0101" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"ADD 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ADD 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        # test "ADD 0101"       add 1 to 0
        Memory.memory[0100] = 0064101    # ADD 0101
        Memory.memory[0101] = 1          # value we are adding to PC
        MainCPU.init()
        MainCPU.AC = 0
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ADD 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ADD 0101" left AC containing %06o, should be 1' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 1, msg)
        msg = '"ADD 0101" modified L to %01o, should be 1' % MainCPU.L
        self.assertTrue(MainCPU.L == 1, msg)
        msg = '"ADD 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)

        # test "ADD 0101"       add 1 to 0177777, L=1 before
        Memory.memory[0100] = 0064101    # ADD 0101
        Memory.memory[0101] = 1          # value we are adding to PC
        MainCPU.init()
        MainCPU.AC = 0177777
        MainCPU.L = 1
        MainCPU.PC = 0100
        MainCPU.running = True
        cycles = MainCPU.execute_one_instruction()
        Trace.itraceend(False)
        msg = '"ADD 0101" used %d cycles, should be 2' % cycles
        self.assertTrue(cycles == 2, msg)
        msg = '"ADD 0101" left AC containing %06o, should be 0' % MainCPU.AC
        self.assertTrue(MainCPU.AC == 0, msg)
        msg = '"ADD 0101" modified L to %01o, should be 0' % MainCPU.L
        self.assertTrue(MainCPU.L == 0, msg)
        msg = '"ADD 0101" modified PC to %06o, should be 0101' % MainCPU.PC
        self.assertTrue(MainCPU.PC== 0101, msg)



################################################################################

if __name__ == '__main__':
    suite = unittest.makeSuite(TestPymlac, 'test')
    runner = unittest.TextTestRunner()
    runner.run(suite)

