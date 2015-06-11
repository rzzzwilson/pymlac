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
#         where <name> is one of AC, L or PC, value is any value
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
#         check register (AC, L or PC) has value <value>
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


from Globals import *
import MainCPU
import Memory


def setreg(name, value):
    """Set register to a value.

    Remember value to check later.
    """

    global RegValues
    
    RegValues[name] = value

    exec "MainCPU.%s = %07o" % (name, value)

def setmem(addr, value):
    """Set memory location to a value."""

    global MemValues

    MemValues[addr] = value

    Memory.memory[addr] = value


def allmem(value):
    """Set all of memory to a value.

    Remember value to check later.
    """

    global MemAllValue

    MemAllValue = value

    for mem in range(PCMASK):
        print str(mem)
        Memory.memory[mem] = value

def allreg(value):
    """Set all registers to a value."""

    global RegAllValue

    RegAllValue = value

    MainCPU.AC = value
    MainCPU.L = value & 1
    MainCPU.PC = value

def execute(test):
    """Execute test string in 'test'."""

    global RegValues, MemValues
    global RegAllValue, MemAllValue
    global Test

    # set globals
    RegValues = {}
    MemValues = {}
    RegAllValue = {}
    MemAllValue = {}

    Test = test

    # clear memory and registers to 0 first
#    allmem(0)
#    allreg(0)

    # interpret the test instructions
    instructions = test.split(';')
    for op in instructions:
        fields = op.split(None, 2)
        op = fields[0].lower()
        try:
            var1 = fields[1]
        except IndexError:
            var1 = None
        try:
            var2 = fields[2]
        except IndexError:
            var2 = None

        try:
            if op == 'setreg':
                setreg(var1, var2)
            elif op == 'setmem':
                setmem(var1, var2)
            elif op == 'run':
                run(var1, var2)
            elif op == 'checkcycles':
                checkcycles(var1, var2)
            elif op == 'checkreg':
                checkreg(var1, var2)
            elif op == 'checkmem':
                checkmem(var1, var2)
            elif op == 'allreg':
                allreg(var1, var2)
            elif op == 'allmem':
                allmem(var1, var2)
            else:
                error('Unrecognized operation: %s' % test)
        except CPUError:
            pass

    # now check all memory and regs for changes
    check_all_mem()
    check_all_regs()

def main(filename):
    """Execute CPU tests from 'filename'."""

    # get all tests from file
    with open(filename, 'rb') as fd:
        lines = fd.readlines()

    # read lines, join continued, get complete tests
    tests = []
    test = ''
    for line in lines:
        line = line[:-1]        # strip newline

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
        execute(test)


################################################################################

if __name__ == '__main__':
    main('CPU.test')
