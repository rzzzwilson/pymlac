#!/usr/bin/python

"""
The Imlac trace stuff.
"""


import time

from Globals import *
import MainCPU
import DisplayCPU

# module-level state variables
tracing = False
tracefile = None


def init(filename):
    global tracing, tracefile

    tracing = True
    tracefile = open(filename, 'w')
    trace('pymlac %s trace\n\n' % PYMLAC_VERSION)
    tracing = False
    comment = None

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

def dtrace(opcode, address=None):
    if tracing:
        if address is None:
            tracefile.write('%s\t\t' % opcode)
        else:
            tracefile.write('%s\t%5.5o\t' % (opcode, address))

def itrace(opcode, indirect=False, address=None):
    if tracing:
        char = '*' if indirect else ''
        if address is None:
            tracefile.write('%s\t%s\t' % (opcode, char))
        else:
            tracefile.write('%s\t%s%5.5o\t' % (opcode, char, address))

def itraceend(dispon):
    if dispon:
        trace('L=%1.1o AC=%6.6o DX=%5.5o DY=%6.6o\n' %
                   (MainCPU.L, MainCPU.AC, DisplayCPU.DX, DisplayCPU.DY))
    else:
        trace('L=%1.1o AC=%6.6o\n' % (MainCPU.L, MainCPU.AC))

def comment(msg):
    tracefile.write(msg+'\n')


def settrace(new_tracing):
    global tracing

    tracing = new_tracing
