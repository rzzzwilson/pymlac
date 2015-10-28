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

# We implement a small interpreter to test the CPU.
# The DSL is documented here: [github.com/rzzzwilson/pymlac].


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

    def str2int(self, string):
        """Convert string to numeric value.

        string  numeric string (decimal or octal)

        Returns the numeric value.
        """

        if string[0] == '0':
            value = int(string, base=8)
        else:
            value = int(string)

        return value

    def assemble(self, addr, opcodes):
        """Assemble a set of instructions, return opcode values.

        addr     address to assemble at
        opcodes  list of ASM lines to assemble

        Returns a list of integer opcodes.
        """

        # split possible multiple instructions
        opcodes = opcodes.split(';')

        # create ASM file with instruction
        with open(self.AsmFilename+'.asm', 'wb') as fd:
            fd.write('\torg\t%07o\n' % addr)
            for line in opcodes:
                fd.write('\t%s\n' % line)
            fd.write('\tend\n')

        # now assemble file
        cmd = ('../iasm/iasm -l %s.lst %s.asm'
               % (self.AsmFilename, self.AsmFilename))
        res = os.system(cmd)

        # read the listing file to get assembled opcode (second line)
        with open(self.AsmFilename+'.lst', 'rb') as fd:
            lines = fd.readlines()

        result = []
        for line in lines[1:-1]:
            (opcode, _) = line.split(None, 1)
            result.append(int(opcode, base=8))

        return result

# Here we implement the DSL primitives.  They all take two parameters which are
# the DSL field1 and field2 values (lowercase strings).  If one or both are
# missing the parameter is None.
#
#   setreg <name> <value>
#   setmem <address> <value>
#   allreg <value>
#   allmem <value>
#   bootrom <type>
#   romwrite <bool>
#   mount <device> <filename>
#   dismount <device>
#   run [<number>]
#   rununtil <address>
#   checklast <device> <value>
#   checkcycles <number>
#   checkreg <name> <value>
#   checkmem <addr> <value>
#   checkcpu <state>
#   checkdcpu <state>

    def setreg(self, name, value):
        """Set register to a value.

        Remember value to check later.
        """

        value = self.str2int(value)

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

    def setmem(self, addr, fld2):
        """Set memory location to a value.

        addr  address of memory location to set
        fld2  value to store at 'addr'
        """

        log.debug('setmem: addr=%s, fld2=%s' % (addr, fld2))

        addr = self.str2int(addr)

        # check if we must assemble var2
        if fld2[0] == '[':
            # assemble one or more instructions
            values = self.assemble(addr, fld2[1:-1])
            log.debug('setmem: assembled opcodes=%s' % str(fld2))
        else:
            values = [self.str2int(fld2)]

        for v in values:
            self.mem_values[addr] = v
            self.memory.put(v, addr, False)
            addr += 1

    def allreg(self, value, ignore):
        """Set all registers to a value."""

        self.reg_all_value = value

        self.cpu.AC = value
        self.cpu.L = value & 1
        self.cpu.PC = value
        self.cpu.DS = value

    def allmem(self, value, ignore):
        """Set all of memory to a value.

        Remember value to check later.
        """

        log.debug('allmem: setting memory to %07o' % value)

        self.mem_all_value = value

        for mem in range(MEMORY_SIZE):
            self.memory.put(value, mem, False)

    def bootrom(loader_type, ignore):
        pass

    def romwrite(writable, ignore):
        pass

    def mount(device, filename):
        pass

    def dismount(device, ignore):
        pass

    def run(self, num_instructions, ignore):
        """Execute one or more instructions.

        num_instructions  number of instructions to execute
        """

        if num_instructions is None:
            # assume number of instructions is 1
            number = 1
        else:
            number = self.str2int(num_instructions)
            if number is None:
                return 'Invalid number of instructions: %s' % num_instructions

        cycles= 0
        for _ in range(number):
            cycles += self.cpu.execute_one_instruction()

        self.used_cycles = cycles

    def rununtil(address, ignore):
        pass

    def checklast(device, value):
        pass

    def checkcycles(self, cycles, ignore):
        """Check that opcode cycles used is correct.

        cycles  expected number of cycles used
        """

        cycles = self.str2int(cycles)

        if cycles != self.used_cycles:
            return ('Run used %d cycles, expected %d'
                    % (self.used_cycles, cycles))

    def checkreg(self, reg, value):
        """Check register is as it should be."""

        if not reg:
            return 'checkreg: requires a register name'

        if value:
            value = self.str2int(value)
        else:
            return 'checkreg: requires a value'

        if reg == 'ac':
            self.reg_values[reg] = self.cpu.AC
            if self.cpu.AC != value:
                return ('AC wrong, is %07o, should be %07o'
                        % (self.cpu.AC, value))
        elif reg == 'l':
            self.reg_values[reg] = self.cpu.L
            if self.cpu.L != value:
                return 'L wrong, is %02o, should be %02o' % (self.cpu.L, value)
        elif reg == 'pc':
            self.reg_values[reg] = self.cpu.PC
            if self.cpu.PC != value:
                return ('PC wrong, is %07o, should be %07o'
                        % (self.cpu.PC, value))
        elif reg == 'ds':
            self.reg_values[reg] = self.cpu.DS
            if self.cpu.DS != value:
                return ('DS wrong, is %07o, should be %07o'
                        % (self.cpu.DS, value))
        else:
            raise Exception('checkreg: bad register name: %s' % name)

    def checkmem(self, addr, value):
        """Check a memory location is as it should be."""

        self.mem_values[addr] = value

        memvalue = self.memory.fetch(addr, False)
        if memvalue != value:
            return ('Memory wrong at address %07o, is %07o, should be %07o'
                    % (addr, memvalue, value))

    def checkcpu(self, state, ignore):
        """Check main CPU run state is as desired."""

        cpu_state = str(self.cpu.running).lower()

        if ((state == "on" and cpu_state != "true") or
            (state == "off" and cpu_state != "false")):
            return ('Main CPU run state is %s, should be %s'
                    % (str(self.cpu.running), str(state)))

    def checkdcpu(self, state, ignore):
        """Check display CPU run state is as desired."""

        dcpu_state = str(self.display.running).lower()

        if ((state == "on" and dcpu_state != "true") or
            (state == "off" and dcpu_state != "false")):
            return ('Display CPU run state is %s, should be %s'
                    % (str(self.cpu.running), str(state)))

# end of DSL primitives

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
        self.reg_all_value = 0
        self.mem_all_value = 0

        result = []

        self.memory = Memory.Memory()
        self.cpu = MainCPU.MainCPU(self.memory, None, None,
                                   None, None, None, None, None)
        self.cpu.running = True
        self.display_state = False

        trace_filename = filename + '.trace'
        Trace.init(trace_filename, self.cpu, None)

        # clear registers and memory to 0 first
        self.allreg(0, None)
        self.allmem(0, None)

        # interpret the test instructions
        suite = test.split(';')
        for instruction in suite:
            fields = instruction.split(None, 2)
            if not fields:
                continue;

            opcode = fields[0].strip().lower()
            if len(fields) == 1:
                fld1 = fld2 = None
            elif len(fields) == 2:
                fld1 = fields[1].strip().lower()
                fld2 = None
            elif len(fields) == 3:
                fld1 = fields[1].strip().lower()
                fld2 = fields[2].strip().lower()

            self.debug_operation(opcode, fld1, fld2)

            # cll the correct DSL primitive
            if opcode == 'setreg':
                r = self.setreg(fld1, fld2)
            elif opcode == 'setmem':
                r = self.setmem(fld1, fld2)
            elif opcode == 'run':
                r = self.run(fld1, fld2)
            elif opcode == 'checkcycles':
                r = self.checkcycles(fld1, fld2)
            elif opcode == 'checkreg':
                r = self.checkreg(fld1, fld2)
            elif opcode == 'checkmem':
                r = self.checkmem(fld1, fld2)
            elif opcode == 'allreg':
                r = self.allreg(fld1, fld2)
            elif opcode == 'allmem':
                r = self.allmem(fld1, fld2)
            elif opcode == 'checkcpu':
                r = self.checkcpu(fld1, fld2)
            elif opcode == 'setd':
                r = self.setd(fld1, fld2)
            elif opcode == 'checkd':
                r = self.checkd(fld1, fld2)
            else:
                raise Exception("Unrecognized opcode '%s' in: %s" % (opcode, test))

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
            line = line[:-1]                # strip newline

            if not line:
                continue                    # skip blank lines

            if line[0] == '#':              # a comment
                continue

            if line[0] in ('\t', ' '):      # continuation
                if test:
                    test += '; '
                test += line[1:]
            else:                           # beginning of new test
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
