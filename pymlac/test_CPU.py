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


import sys
import os

from Globals import *
import MainCPU
import Memory
import PtrPtp
import Trace

import log
log = log.Log('test_CPU.log', log.Log.DEBUG)


class TestCPU(object):

    # temporary assembler file and listfile prefix
    AsmFilename = '_#ASM#_'
    ProgressChar = '|\\-/'
    ProgressCount = 0


    def __init__(self):
        """Initialize the test."""

        pass

    def show_progress(self):
        """Show progress to stdout.  A spinning line."""

        print '%s\r' % self.ProgressChar[self.ProgressCount],
        self.ProgressCount += 1
        if self.ProgressCount >= len(self.ProgressChar):
            self.ProgressCount = 0
        sys.stdout.flush()

    def list2int(self, values):
        """Convert a string of multiple values to a list of ints.

        values  a string like: '123;4;-2'
                (could be just '5')

        Returns a list of integers, for example: [123, 4, -2]
        """

        values = values.split(';')

        result = []
        for value in values:
            result.append(self.str2int(value))

        return result

    def str2int(self, string):
        """Convert string to numeric value.

        string  numeric string (decimal or octal)

        Returns the numeric value.
        """

        try:
            if string[0] == '0':
                value = int(string, base=8)
            else:
                value = int(string)
        except:
            return None

        return value

    def assemble(self, addr, opcodes):
        """Assemble a set of instructions, return opcode values.

        addr     address to assemble at
        opcodes  list of ASM lines to assemble

        Returns a list of integer opcodes.
        """

        # split possible multiple instructions
        opcodes = opcodes.split('|')

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
#   run [<number>]
#   rununtil <address>
#   checkcycles <number>
#   checkreg <name> <value>
#   checkmem <addr> <value>
#   checkcpu <state>
#   checkdcpu <state>
#   mount <device> <filename>
#   dismount <device>
#   checkfile <file1> <file2>

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

    def setmem(self, addr, values):
        """Set memory location to a value.

        addr    address of memory location to set
        values  value to store at 'addr'
        """

        addr = self.str2int(addr)

        # check if we must assemble values
        if values[0] == '[':
            # assemble one or more instructions
            values = self.assemble(addr, values[1:-1])
        else:
            values = self.list2int(values)

        for v in values:
            self.mem_values[addr] = v
            self.memory.put(v, addr, False)
            addr += 1

    def allreg(self, value, ignore):
        """Set all registers to a value."""

        new_value = self.str2int(value)
        if new_value is None:
            return 'allreg: bad value: %s' % str(value)

        self.reg_all_value = new_value

        self.cpu.AC = new_value
        self.cpu.L = new_value & 1
        self.cpu.PC = new_value
        self.cpu.DS = new_value

    def allmem(self, value, ignore):
        """Set all of memory to a value.

        Remember value to check later.
        """

        new_value = self.str2int(value)
        if new_value is None:
            return 'allmem: bad value: %s' % str(value)

        self.mem_all_value = new_value

        for mem in range(MEMORY_SIZE):
            self.memory.put(new_value, mem, False)

    def bootrom(loader_type, ignore):
        """Set bootloader memory range to appropriate bootloader code.

        loader_type  either 'ptr' or 'tty'
        """

        if loader_type not in ['ptr', 'tty']:
            return 'bootrom: invalid bootloader type: %s' % loader_type
        self.memory.set_ROM(loader_type)

    def romwrite(writable, ignore):
        """Set ROM to be writable or not."""

        self.memory.rom_protected = writable

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

        self.used_cycles= 0
        for _ in range(number):
            cycles = self.cpu.execute_one_instruction()
            self.ptrptp.ptr_tick(cycles)
            self.ptrptp.ptp_tick(cycles)
            self.used_cycles += cycles


    def rununtil(self, address, ignore):
        """Execute instructions until PC == address.

        address  address at which to stop

        We allow PC to be stop address first instruction.
        We stop after that if PC == address.
        """

        new_address = self.str2int(address)
        if new_address is None:
            return 'rununtil: invalid stop address: %s' % address

        self.used_cycles= 0
        while True:
            cycles = self.cpu.execute_one_instruction()
            self.ptrptp.ptr_tick(cycles)
            self.ptrptp.ptp_tick(cycles)
            self.used_cycles += cycles
            if self.cpu.PC == new_address:
                break

    def checkcycles(self, cycles, ignore):
        """Check that opcode cycles used is correct.

        cycles  expected number of cycles used
        """

        num_cycles = self.str2int(cycles)
        if num_cycles is None:
            return 'checkcycles: invalid number of cycles: %s' % cycles

        if num_cycles != self.used_cycles:
            return ('Run used %d cycles, expected %d'
                    % (self.used_cycles, num_cycles))

    def checkreg(self, reg, value):
        """Check register is as it should be."""

        new_value = self.str2int(value)
        if new_value is None:
            return 'checkreg: bad value: %s' % str(value)

        if reg == 'ac':
            self.reg_values[reg] = self.cpu.AC
            if self.cpu.AC != new_value:
                return ('AC wrong, is %07o, should be %07o'
                        % (self.cpu.AC, new_value))
        elif reg == 'l':
            self.reg_values[reg] = self.cpu.L
            if self.cpu.L != new_value:
                return ('L wrong, is %02o, should be %02o'
                        % (self.cpu.L, new_value))
        elif reg == 'pc':
            self.reg_values[reg] = self.cpu.PC
            if self.cpu.PC != new_value:
                return ('PC wrong, is %07o, should be %07o'
                        % (self.cpu.PC, new_value))
        elif reg == 'ds':
            self.reg_values[reg] = self.cpu.DS
            if self.cpu.DS != new_value:
                return ('DS wrong, is %07o, should be %07o'
                        % (self.cpu.DS, new_value))
        else:
            return 'checkreg: bad register name: %s' % str(name)

    def checkmem(self, addr, value):
        """Check a memory location is as it should be."""

        new_addr = self.str2int(addr)
        if new_addr is None:
            return 'checkmem: bad address: %s' % str(addr)
        new_value = self.str2int(value)
        if new_value is None:
            return 'checkmem: bad value: %s' % str(value)

        self.mem_values[new_addr] = new_value

        memvalue = self.memory.fetch(new_addr, False)
        if memvalue != new_value:
            return ('Memory wrong at address %07o, is %07o, should be %07o'
                    % (new_addr, memvalue, new_value))

    def checkcpu(self, state, ignore):
        """Check main CPU run state is as desired."""

        if state not in ('on', 'off'):
            return 'checkcpu: bad state: %s' % str(state)

        cpu_state = str(self.cpu.running).lower()

        if ((state == "on" and cpu_state != "true") or
            (state == "off" and cpu_state != "false")):
            return ('Main CPU run state is %s, should be %s'
                    % (str(self.cpu.running), str(state)))

    def checkdcpu(self, state, ignore):
        """Check display CPU run state is as desired."""

        if state not in ('on', 'off'):
            return 'checkdcpu: bad state: %s' % str(state)

        dcpu_state = str(self.display.running).lower()

        if ((state == "on" and dcpu_state != "true") or
            (state == "off" and dcpu_state != "false")):
            return ('Display CPU run state is %s, should be %s'
                    % (str(self.cpu.running), str(state)))

    def mount(self, device, filename):
        """Mount a file on a device.

        device    name of device
        filename  path to file to mount

        If the device is an input device, the file must exist.
        """

        if device == 'ptr':
            if not os.path.exists(filename) or not os.path.isfile(filename):
                return "mount: '%s' doesn't exist or isn't a file" % filename
            self.ptrptp.ptr_mount(filename)
        elif device == 'ptp':
            self.ptrptp.ptp_mount(filename)
        else:
            return 'mount: bad device: %s' % device

    def dismount(self, device):
        """Dismount a file from a device.

        device    name of device
        """

        if device == 'ptr':
            self.ptrptp.ptr_dismount()
        elif device == 'ptp':
            self.ptrptp.ptp_dismount()
        else:
            return 'dismount: bad device: %s' % device

    def checkfile(self, file1, file2):
        """Compare two files, error if different."""

        cmd = 'cmp -s %s %s' % (file1, file2)
        res = os.system(cmd) & 0xff
        if res:
            return 'Files %s and %s are different' % (file1, file2)

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
        self.ptrptp = PtrPtp.PtrPtp()
        self.cpu = MainCPU.MainCPU(self.memory, None, None,
                                   None, None, None, self.ptrptp)
        self.cpu.running = True
        self.display_state = False

        trace_filename = filename + '.trace'
        Trace.init(trace_filename, self.cpu, None)

        # clear registers and memory to 0 first
        self.allreg(self.reg_all_value, None)
        self.allmem(self.mem_all_value, None)

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
            elif opcode == 'rununtil':
                r = self.rununtil(fld1, fld2)
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
            elif opcode == 'checkdcpu':
                r = self.checkdcpu(fld1, fld2)
            elif opcode == 'setd':
                r = self.setd(fld1, fld2)
            elif opcode == 'bootrom':
                r = self.bootrom(fld1, fld2)
            elif opcode == 'romwrite':
                r = self.romwrite(fld1, fld2)
            elif opcode == 'mount':
                r = self.mount(fld1, fld2)
            elif opcode == 'dismount':
                r = self.dismount(fld1, fld2)
            elif opcode == 'checkfile':
                r = self.checkfile(fld1, fld2)
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
            self.show_progress()

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
            self.show_progress()
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
