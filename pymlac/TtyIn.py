#!/usr/bin/python 

"""
Emulate the Input TTY (TTYIN).
"""

from Globals import *


# define various internal states
DEVICE_NOT_READY = 0
DEVICE_READY = 1
TTYIN_CHARS_PER_SECOND = 1000
DEVICE_READY_CYCLES = int(CYCLES_PER_SECOND / TTYIN_CHARS_PER_SECOND)

# module-level state variables
filename = None
open_file = None
value = 0
atEOF = 1
cycle_count = 0
isready = DEVICE_NOT_READY


def init():
    global filename, open_file, value, atEOF, cycle_count, isready

    filename = None
    open_file = None
    value = 0
    atEOF = 1
    cycle_count = 0
    isready = DEVICE_NOT_READY

def mount(fname):
    global filename, open_file, value, atEOF, cycle_count, isready

    filename = fname
    open_file = open(filename, 'r')
    value = 0
    atEOF = 0
    cycle_count = DEVICE_READY_CYCLES
    isready = DEVICE_NOT_READY

def dismount():
    global filename, open_file, value, atEOF, cycle_count, isready

    if open_file:
        open_file.close()
    filename = None
    open_file = None
    value = 0
    atEOF = 1
    isready = DEVICE_NOT_READY

def read():
    return value

def ready():
    return (isready == DEVICE_READY)

def clear():
    global filename, open_file, value, atEOF, cycle_count, isready

    isready = DEVICE_NOT_READY

def tick(cycles):
    global filename, open_file, value, atEOF, cycle_count, isready

    if (not atEOF):
        cycle_count -= cycles
        if cycle_count <= 0:
            cycle_count = DEVICE_READY_CYCLES
            value = open_file.read(1)
            isready = DEVICE_READY
            if len(value) < 1:
                atEOF = 1
                value = 0
                cycle_count = 0
                isready = DEVICE_NOT_READY

