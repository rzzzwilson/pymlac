#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test pymlac CPU opcodes DIRECTLY.

Usage: test_CPU.py [<options>] <filename>

where <filename> is a file of test instructions and
      <options> is one or more of
          -h    prints this help and stops
"""

import time

# We implement a small interpreter to test the CPU.  The test code is read in
# from a file:
#
#    # LAW
#    setreg ac 012345; setreg l 1; setreg pc 0100; setmem 0100 [LAW 0]; RUN; checkcycles 1; checkreg pc 0101; checkreg ac 0
#    setreg ac 012345; setreg l 0; setmem 0100 [LAW 0]; RUN 0100
#            checkcycles 1; checkreg pc 0101; checkreg ac 0
#
# The instructions are delimited by ';' characters.  A line beginning with a
# TAB character is a continuation of the previous line.
# Lines with '#' in column 1 are comments.
#
# The test instructions are:
#     setreg <name> <value>
#         where <name> is one of AC, L, PC or DS, value is any value
#         (all registers are set to 0 initially)
#
#     setmem <addr> <value>
#         where <addr> is an address and value is any value OR
#         [<instruction>] where the value is the assembled opcode
#
#     run [<addr>]
#         execute one instruction, if optional <addr> is used PC := addr before
#
#     checkcycles <number>
#         check number of executed cycles is <number>
#
#     checkreg <name> <value>
#         check register (AC, L, PC or DS) has value <value>
#
#     checkmem <addr> <value>
#         check that memory at <addr> has <value>
#
#     allreg <value>
#         sets all registers to <value>
#         a "allreg 0" is assumed before each test
#
#     allmem <value>
#         sets all of memory to <value>
#         a "allmem 0" is assumed before each test
#
# In addition, all of memory is checked for changed values after execution
# except where an explicit "checkmem <addr> <value>" has been performed.
# Additionally, registers that aren't explicitly checked are tested to make
# sure they didn't change.
#
# If a test line finds no error, just print the fully assembled test line.
# If any errors are found, print line followed by all errors.


import os

from Globals import *
import MainCPU
import Memory
import Trace

import log
log = log.Log('test_CPU.log', log.Log.DEBUG)


class TestCPU(object):

    # temporary assembler file and listfile prefix
    AsmFilename = '_#ASM#_'


    def __init__(self):
        """Initialize the test."""

        pass

    def assemble(self, addr, opcode):
        """Assemble a single instruction, return opcode."""

        # create ASM file with instruction
        with open(self.AsmFilename+'.asm', 'wb') as fd:
            fd.write('\torg\t%07o\n' % addr)
            fd.write('\t%s\n' % opcode[1:-1])
            fd.write('\tend\n')

        # now assemble file
        #cmd = '../iasm/iasm -l %s.lst %s.asm >xyzzy 2>&1' % (self.AsmFilename, self.AsmFilename)
        cmd = '../iasm/iasm -l %s.lst %s.asm' % (self.AsmFilename, self.AsmFilename)
        res = os.system(cmd)

        # read the listing file to get assembled opcode (second line)
        with open(self.AsmFilename+'.lst', 'rb') as fd:
            lines = fd.readlines()
        line = lines[1]
        (opcode, _) = line.split(None, 1)

        return int(opcode, base=8)


    def setreg(self, name, value):
        """Set register to a value.

        Remember value to check later.
        """

        self.reg_values[name] = value

        if name == 'ac':
            self.cpu.AC = value
        elif name == 'l':
            self.cpu.L = value & 1
        elif name == 'pc':
            self.cpu.PC = value
        elif name == 'ds':
            self.cpu.DS = value
        else:
            raise Exception('setreg: bad register name: %s' % name)

    def setmem(self, addr, value):
        """Set memory location to a value."""

        if isinstance(value, basestring):
            log.debug('setmem: addr=%s, value=%s' % (oct(addr), value))
        else:
            log.debug('setmem: addr=%s, value=%s' % (oct(addr), oct(value)))

        # check if we must assemble var2
        if isinstance(value, basestring) and value[0] == '[':
            # assemble an instruction
            value = self.assemble(addr, value)
            log.debug('setmem: assembled opcode=%07o' % value)

        self.mem_values[addr] = value
        log.debug('setmem: After, MemValues=%s' % str(self.mem_values))

        self.memory.put(value, addr, False)
        log.debug('setmem: After, Memory at %07o is %07o' % (addr, self.memory.fetch(addr, False)))

    def allmem(self, value, ignore=None):
        """Set all of memory to a value.

        Remember value to check later.
        """

        log.debug('allmem: setting memory to %07o' % value)

        self.mem_all_value = value

        for mem in range(MEMORY_SIZE):
            self.memory.put(value, mem, False)

    def allreg(self, value):
        """Set all registers to a value."""

        self.reg_all_value = value

        self.cpu.AC = value
        self.cpu.L = value & 1
        self.cpu.PC = value
        self.cpu.DS = value

    def check_all_mem(self):
        """Check memory for unwanted changes."""

        result = []

        for mem in range(MEMORY_SIZE):
            value = self.memory.fetch(mem, False)
            if mem in self.mem_values:
                if value != self.mem_values[mem]:
                    result.append('Memory at %07o changed, is %07o, should be %07o'
                                  % (mem, value, self.mem_values[mem]))
            else:
                if value != self.mem_all_value:
                    print('mem: %s, value: %s, self.mem_all_value: %s'
                          % (str(type(mem)), str(type(value)), str(type(self.mem_all_value))))
                    result.append('Memory at %07o changed, is %07o, should be %07o'
                                  % (mem, value, self.mem_all_value))

    def check_all_regs(self):
        """Check registers for unwanted changes."""

        result = []

        if 'ac' in self.reg_values:
            if self.cpu.AC != self.reg_values['ac']:
                result.append('AC changed, is %07o, should be %07o'
                              % (self.cpu.AC, self.reg_values['ac']))
        else:
            if self.cpu.AC != self.reg_all_value:
                result.append('AC changed, is %07o, should be %07o'
                              % (self.cpu.AC, self.reg_all_value))

        if 'l' in self.reg_values:
            if self.cpu.L != self.reg_values['l']:
                result.append('L changed, is %02o, should be %02o'
                              % (self.cpu.L, self.reg_values['l']))
        else:
            if self.cpu.L != self.reg_all_value & 1:
                result.append('L changed, is %02o, should be %02o'
                              % (self.cpu.L, self.reg_all_value & 1))

        if 'pc' in self.reg_values:
            if self.cpu.PC != self.reg_values['pc']:
                result.append('PC changed, is %07o, should be %07o'
                              % (self.cpu.PC, self.reg_values['pc']))
        else:
            if self.cpu.PC != self.reg_all_value:
                result.append('PC changed, is %07o, should be %07o'
                              % (self.cpu.PC, self.reg_all_value))

        if 'ds' in self.reg_values:
            if self.cpu.DS != self.reg_values['ds']:
                result.append('DS changed, is %07o, should be %07o'
                              % (self.cpu.DS, self.reg_values['ds']))
        else:
            if self.cpu.DS != self.reg_all_value:
                result.append('DS changed, is %07o, should be %07o'
                              % (self.cpu.DS, self.reg_all_value))

        return result

    def checkreg(self, reg, value):
        """Check register is as it should be."""

        if reg == 'ac':
            self.reg_values[reg] = self.cpu.AC
            if self.cpu.AC != value:
                return 'AC wrong, is %07o, should be %07o' % (self.cpu.AC, value)
        elif reg == 'l':
            self.reg_values[reg] = self.cpu.L
            if self.cpu.L != value:
                return 'L wrong, is %02o, should be %02o' % (self.cpu.L, value)
        elif reg == 'pc':
            self.reg_values[reg] = self.cpu.PC
            if self.cpu.PC != value:
                return 'PC wrong, is %07o, should be %07o' % (self.cpu.PC, value)
        elif reg == 'ds':
            self.reg_values[reg] = self.cpu.DS
            if self.cpu.DS != value:
                return 'DS wrong, is %07o, should be %07o' % (self.cpu.DS, value)
        else:
            raise Exception('checkreg: bad register name: %s' % name)

    def checkmem(self, addr, value):
        """Check a memory location is as it should be."""

        self.mem_values[addr] = value
        log.debug('checkmem: After, MemValues=%s' % str(self.mem_values))

        memvalue = self.memory.fetch(addr, False)
        if memvalue != value:
            return 'Memory wrong at address %07o, is %07o, should be %07o' % (addr, memvalue, value)

    def checkcycles(self, cycles, var2=None):
        """Check that opcode cycles used is correct."""

        if cycles != self.used_cycles:
            return 'Opcode used %d cycles, expected %d' % (self.used_cycles, cycles)

    def run(self, addr, var2):
        """Execute instruction."""

        if addr is not None:
            # force PC to given address
            self.setreg('pc', addr)

        self.used_cycles = self.cpu.execute_one_instruction()

    def checkrun(self, state, var2):
        """Check CPU run state is as desired."""

        if str(self.cpu.running).lower() != state:
            return 'CPU run state is %s, should be %s' % (str(self.cpu.running), str(state))

    def setd(self, state, var2):
        """Set display state."""

        if state == 'on':
            self.display_state = True
        elif state == 'off':
            self.display_state = False
        else:
            raise Exception('setd: bad state: %s' % str(state))

    def checkd(self, state, var2):
        """Check display state is as expected."""

        if state == 'on' and self.display_state is not True:
            return 'DCPU run state is %s, should be True' % str(self.display_state)
        if state == 'off' and self.display_state is True:
            return 'DCPU run state is %s, should be False' % str(self.display_state)

    def debug_operation(self, op, var1, var2):
        """Write operation to log file."""

        if var1:
            if var2:
                log.debug('Operation: %s %s %s' % (op, var1, var2))
            else:
                log.debug('Operation: %s %s' % (op, var1))
        else:
            log.debug('Operation: %s' % op)

    def execute(self, test, filename):
        """Execute test string in 'test'."""

        # set globals
        self.reg_values = {}
        self.mem_values = {}
        #self.reg_all_value = {}
        #self.mem_all_value = {}
        self.reg_all_value = 0
        self.mem_all_value = 0

        result = []

        self.memory = Memory.Memory()
        self.cpu = MainCPU.MainCPU(self.memory, None, None, None, None, None, None, None)
        self.cpu.running = True
        self.display_state = False

        trace_filename = filename + '.trace'
        Trace.init(trace_filename, self.cpu, None)

        # clear registers to 0 first
        self.allreg(0)

        # interpret the test instructions
        instructions = test.split(';')
        for op in instructions:
            fields = op.split(None, 2)
            op = fields[0].lower()
            try:
                var1 = fields[1].lower()
            except IndexError:
                var1 = None
            try:
                var2 = fields[2].lower()
            except IndexError:
                var2 = None

            self.debug_operation(op, var1, var2)

            # change var strings into numeric values
            if var1 and var1[0] in '0123456789':
                if var1[0] == '0':
                    var1 = int(var1, base=8)
                else:
                    var1 = int(var1)
                var1 &= 0177777

            if var2 and var2[0] in '0123456789':
                if var2[0] == '0':
                    var2 = int(var2, base=8)
                else:
                    var2 = int(var2)
                var2 &= 0177777

            if op == 'setreg':
                r = self.setreg(var1, var2)
            elif op == 'setmem':
                r = self.setmem(var1, var2)
            elif op == 'run':
                r = self.run(var1, var2)
            elif op == 'checkcycles':
                r = self.checkcycles(var1, var2)
            elif op == 'checkreg':
                r = self.checkreg(var1, var2)
            elif op == 'checkmem':
                r = self.checkmem(var1, var2)
            elif op == 'allreg':
                r = self.allreg(var1, var2)
            elif op == 'allmem':
                r = self.allmem(var1, var2)
            elif op == 'checkrun':
                r = self.checkrun(var1, var2)
            elif op == 'setd':
                r = self.setd(var1, var2)
            elif op == 'checkd':
                r = self.checkd(var1, var2)
            else:
                raise Exception("Unrecognized operation '%s' in: %s" % (op, test))

            if r is not None:
                result.append(r)

        # now check all memory and regs for changes
        r = self.check_all_mem()
        if r:
            result.append(r)

        r = self.check_all_regs()
        if r:
            result.extend(r)

        if result:
            print(test)
            print('\t' + '\n\t'.join(result))

        self.memdump('core.txt', 0, 0200)

    def memdump(self, filename, start, number):
        """Dump memory from 'start' into 'filename', 'number' words dumped."""

        with open(filename, 'wb') as fd:
            for addr in range(start, start+number, 8):
                a = addr
                llen = min(8, start+number - addr)
                line = '%04o  ' % addr
                for _ in range(llen):
                    line += '%06o ' % self.memory.fetch(a, False)
                    a += 1
                fd.write('%s\n' % line)

    def main(self, filename):
        """Execute CPU tests from 'filename'."""

        log.debug("Running test file '%s'" % filename)

        # get all tests from file
        with open(filename, 'rb') as fd:
            lines = fd.readlines()

        # read lines, join continued, get complete tests
        tests = []
        test = ''
        for line in lines:
            line = line[:-1]        # strip newline
            if not line:
                continue            # skip blank lines

            if line[0] == '#':      # a comment
                continue

            if line[0] == '\t':     # continuation
                if test:
                    test += '; '
                test += line[1:]
            else:                   # beginning of new test
                if test:
                    tests.append(test)
                test = line

        # flush last test
        if test:
            tests.append(test)

        # now do each test
        for test in tests:
            log.debug('Executing test: %s' % test)
            self.execute(test, filename)

################################################################################

if __name__ == '__main__':
    import sys
    import getopt

    def usage(msg=None):
        if msg:
            print('*'*60)
            print(msg)
            print('*'*60)
        print(__doc__)

    try:
        (opts, args) = getopt.gnu_getopt(sys.argv, "h", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(10)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    if len(args) != 2:
        usage()
        sys.exit(10)

    filename = args[1]
    try:
        f = open(filename)
    except IOError:
        print("Sorry, can't find file '%s'" % filename)
        sys.exit(10)
    f.close()

    test = TestCPU()
    test.main(filename)
