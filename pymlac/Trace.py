#!/usr/bin/python

"""
The Imlac trace stuff.
"""


import time

from Globals import *

# module-level state variables
tracing = False
tracefile = None
cpu = None
dcpu = None


def init(filename, maincpu, displaycpu):
    global tracing, tracefile, cpu, dcpu

    tracing = True
    tracefile = open(filename, 'w')
    trace('%s trace\n%s\n' % (PYMLAC_VERSION, '-'*60))
    tracing = False
    comment = None

    cpu = maincpu
    dcpu = displaycpu

def close():
    import tracing, tracefile

    tracefile.close()
    tracing = False
    tracefile = None

def trace(msg):
    if tracing:
        tracefile.write(msg)
    
def deimtrace(opcode, code):
    if tracing:
        tracefile.write('%s\t%s\t' % (opcode, code))
        tracefile.flush()

def dtrace(opcode, address=None):
    if tracing:
        if address is None:
            tracefile.write('%s\t\t' % opcode)
        else:
            tracefile.write('%s\t%5.5o\t' % (opcode, address))
        tracefile.flush()

def itrace(opcode, indirect=False, address=None):
    if tracing:
        char = '*' if indirect else ''
        if address is None:
            tracefile.write('%s\t%s\t' % (opcode, char))
        else:
            tracefile.write('%s\t%s%5.5o\t' % (opcode, char, address))
        tracefile.flush()

def itraceend(dispon):
    if dispon:
        trace('L=%1.1o AC=%6.6o DX=%5.5o DY=%6.6o\n' %
                   (cpu.L, cpu.AC, dcpu.DX, dcpu.DY))
    else:
        trace('L=%1.1o AC=%6.6o\n' % (cpu.L, cpu.AC))
    tracefile.flush()

def comment(msg):
    tracefile.write(msg+'\n')
    tracefile.flush()

def settrace(new_tracing):
    global tracing

    tracing = new_tracing
