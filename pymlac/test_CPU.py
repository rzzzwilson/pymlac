#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test pymlac CPU opcodes DIRECTLY.

Usage: test_CPU.py [<options>] <filename>

where <filename> is a file of test instructions and
      <options> is one or more of
          -h    prints this help and stops
"""

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

import log
log = log.Log('test_CPU.log', log.Log.DEBUG)


# number of cycles used in previous instruction
UsedCycles = 0

# register+value explicitly set by test
RegValues = {}

# memory address+value explicitly set by test
MemValues = {}

# memory value all explicitly set to (shouldn't change)
MemAllValue = None

# registers value all explicitly set to (shouldn't change)
RegAllValue = None

# temporary assembler file and listfile prefix
AsmFilename = '_#ASM#_'


def assemble(addr, opcode):
    """Assemble a single instruction, return opcode."""

    # create ASM file with instruction
    with open(AsmFilename+'.asm', 'wb') as fd:
        fd.write('\torg\t%07o\n' % addr)
        fd.write('\t%s\n' % opcode[1:-1])
        fd.write('\tend\n')

    # now assemble file
    os.system('../iasm/iasm -l %s.lst %s.asm' % (AsmFilename, AsmFilename))

    # read the listing file to get assembled opcode (second line)
    with open(AsmFilename+'.lst', 'rb') as fd:
        lines = fd.readlines()
    line = lines[1]
    (opcode, _) = line.split(None, 1)

    return int(opcode, base=8)


def setreg(name, value):
    """Set register to a value.

    Remember value to check later.
    """

    global RegValues
    
    RegValues[name] = value

    if name == 'ac':
        MainCPU.AC = value
    elif name == 'l':
        MainCPU.L = value & 1
    elif name == 'pc':
        MainCPU.PC = value
    elif name == 'ds':
        MainCPU.DS = value
    else:
        raise Exception('setreg: bad register name: %s' % name)

def setmem(addr, value):
    """Set memory location to a value."""

    if isinstance(value, basestring):
        log.debug('setmem: addr=%s, value=%s' % (oct(addr), value))
    else:
        log.debug('setmem: addr=%s, value=%s' % (oct(addr), oct(value)))

    global MemValues

    # check if we must assemble var2
    if isinstance(value, basestring) and value[0] == '[':
        # assemble an instruction
        value = assemble(addr, value)
        log.debug('setmem: assembled opcode=%07o' % value)

    MemValues[addr] = value
    log.debug('setmem: After, MemValues=%s' % str(MemValues))

    Memory.put(value, addr, False)
    log.debug('setmem: After, Memory at %07o is %07o' % (addr, Memory.fetch(addr, False)))


def allmem(value):
    """Set all of memory to a value.

    Remember value to check later.
    """

    global MemAllValue

    log.debug('allmem: setting memory to %07o' % value)

    MemAllValue = value

    for mem in range(MEMORY_SIZE):
        Memory.put(value, mem, False)

def allreg(value):
    """Set all registers to a value."""

    global RegAllValue

    RegAllValue = value

    MainCPU.AC = value
    MainCPU.L = value & 1
    MainCPU.PC = value
    MainCPU.DS = value

def check_all_mem():
    """Check memory for unwanted changes."""

    result = []

    for mem in range(MEMORY_SIZE):
        value = Memory.fetch(mem, False)
        if mem in MemValues:
            if value != MemValues[mem]:
                result.append('Memory at %07o changed, is %07o, should be %07o'
                              % (mem, value, MemValues[mem]))
        else:
            if value != MemAllValue:
                result.append('Memory at %07o changed, is %07o, should be %07o'
                              % (mem, value, MemAllValue))

def check_all_regs():
    """Check registers for unwanted changes."""

    result = []

    if 'ac' in RegValues:
        if MainCPU.AC != RegValues['ac']:
            result.append('AC changed, is %07o, should be %07o'
                          % (MainCPU.AC, RegValues['ac']))
    else:
        if MainCPU.AC != RegAllValue:
            result.append('AC changed, is %07o, should be %07o'
                          % (MainCPU.AC, RegAllValue))

    if 'l' in RegValues:
        if MainCPU.L != RegValues['l']:
            result.append('L changed, is %02o, should be %02o'
                          % (MainCPU.L, RegValues['l']))
    else:
        if MainCPU.L != RegAllValue & 1:
            result.append('L changed, is %02o, should be %02o'
                          % (MainCPU.L, RegAllValue & 1))

    if 'pc' in RegValues:
        if MainCPU.PC != RegValues['pc']:
            result.append('PC changed, is %07o, should be %07o'
                          % (MainCPU.PC, RegValues['pc']))
    else:
        if MainCPU.PC != RegAllValue:
            result.append('PC changed, is %07o, should be %07o'
                          % (MainCPU.PC, RegAllValue))

    if 'ds' in RegValues:
        if MainCPU.DS != RegValues['ds']:
            result.append('DS changed, is %07o, should be %07o'
                          % (MainCPU.DS, RegValues['ds']))
    else:
        if MainCPU.DS != RegAllValue:
            result.append('DS changed, is %07o, should be %07o'
                          % (MainCPU.DS, RegAllValue))

    return result

def checkreg(reg, value):
    """Check register is as it should be."""
    
    global RegValues

    if reg == 'ac':
        RegValues[reg] = MainCPU.AC
        if MainCPU.AC != value:
            return 'AC wrong, is %07o, should be %07o' % (MainCPU.AC, value)
    elif reg == 'l':
        RegValues[reg] = MainCPU.L
        if MainCPU.L != value:
            return 'L wrong, is %02o, should be %02o' % (MainCPU.L, value)
    elif reg == 'pc':
        RegValues[reg] = MainCPU.PC
        if MainCPU.PC != value:
            return 'PC wrong, is %07o, should be %07o' % (MainCPU.PC, value)
    elif reg == 'ds':
        RegValues[reg] = MainCPU.DS
        if MainCPU.DS != value:
            return 'DS wrong, is %07o, should be %07o' % (MainCPU.DS, value)
    else:
        raise Exception('checkreg: bad register name: %s' % name)

def checkmem(addr, value):
    """Check a memory location is as it should be."""

    global MemValues

    MemValues[addr] = value
    log.debug('checkmem: After, MemValues=%s' % str(MemValues))

    memvalue = Memory.fetch(addr, False)
    if memvalue != value:
        return 'Memory wrong at address %07o, is %07o, should be %07o' % (addr, memvalue, value)

def checkcycles(cycles, var2=None):
    """Check that opcode cycles used is correct."""

    if cycles != UsedCycles:
        return 'Opcode used %d cycles, expected %d' % (UsedCycles, cycles)

def run(addr, var2):
    """Execute instruction."""

    global UsedCycles

    if addr is not None:
        # force PC to given address
        setreg('pc', addr)

    UsedCycles = MainCPU.execute_one_instruction()

def checkrun(state, var2):
    """Check CPU run state is as desired."""

    if str(MainCPU.running).lower() != state:
        return 'CPU run state should be %s, is %s' % (str(state), str(MainCPU.running))

def debug_operation(op, var1, var2):
    """Write operation to log file."""

    if var1:
        if var2:
            log.debug('Operation: %s %s %s' % (op, var1, var2))
        else:
            log.debug('Operation: %s %s' % (op, var1))
    else:
        log.debug('Operation: %s' % op)

def execute(test):
    """Execute test string in 'test'."""

    global RegValues, MemValues
    global RegAllValue, MemAllValue

    # set globals
    RegValues = {}
    MemValues = {}
    RegAllValue = {}
    MemAllValue = {}

    result = []

    MainCPU.init()
    MainCPU.running = True
    Memory.init()

    # clear memory and registers to 0 first
    allmem(0)
    allreg(0)

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

        debug_operation(op, var1, var2)

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
            r = setreg(var1, var2)
        elif op == 'setmem':
            r = setmem(var1, var2)
        elif op == 'run':
            r = run(var1, var2)
        elif op == 'checkcycles':
            r = checkcycles(var1, var2)
        elif op == 'checkreg':
            r = checkreg(var1, var2)
        elif op == 'checkmem':
            r = checkmem(var1, var2)
        elif op == 'allreg':
            r = allreg(var1, var2)
        elif op == 'allmem':
            r = allmem(var1, var2)
        elif op == 'checkrun':
            r = checkrun(var1, var2)
        else:
            raise Exception('Unrecognized operation: %s' % test)

        if r is not None:
            result.append(r)


    # now check all memory and regs for changes
    r = check_all_mem()
    if r:
        result.append(r)

    r = check_all_regs()
    if r:
        result.extend(r)

    if result:
        print(test)
        print('\t' + '\n\t'.join(result))

    memdump('core.txt', 0, 0200)

def memdump(filename, start, number):
    """Dump memory from 'start' into 'filename', 'number' words dumped."""

    with open(filename, 'wb') as fd:
        for addr in range(start, start+number, 8):
            a = addr
            llen = min(8, start+number - addr)
            line = '%04o  ' % addr
            for _ in range(llen):
                line += '%06o ' % Memory.fetch(a, False)
                a += 1
            fd.write('%s\n' % line)

def main(filename):
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
        execute(test)


################################################################################

if __name__ == '__main__':
    main('CPU.test')
