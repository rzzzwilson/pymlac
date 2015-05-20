#!/usr/bin/python 

"""
Emulate the Output TTY (TTYOUT).
"""


from Globals import *


# define various internal states
DEVICE_NOT_READY = 0
DEVICE_READY = 1
TTYOUT_CHARS_PER_SECOND = 1000
DEVICE_NOT_READY_CYCLES = int(CYCLES_PER_SECOND / TTYOUT_CHARS_PER_SECOND)

# module-level state variables
filename = None
open_file = None
open_file = 0
cycle_count = 0
state = DEVICE_NOT_READY


def init():
    global filename, open_file, open_file, cycle_count, state

    filename = None
    open_file = None
    open_file = 0
    cycle_count = 0
    state = DEVICE_NOT_READY

def mount(fname):
    global filename, open_file, open_file, cycle_count, state

    filename = fname
    open_file = open(filename, 'w')
    state = DEVICE_READY

def dismount():
    global filename, open_file, open_file, cycle_count, state

    if open_file:
        open_file.close()
    filename = None
    open_file = None
    state = DEVICE_NOT_READY

def write(char):
    global filename, open_file, open_file, cycle_count, state

    open_file.write(char)
    cycle_count = DEVICE_NOT_READY_CYCLES

def ready():
    return (state != DEVICE_NOT_READY)

def clear():
    global filename, open_file, open_file, cycle_count, state

    state = DEVICE_NOT_READY

def tick(cycles):
    global filename, open_file, open_file, cycle_count, state

    if (state == DEVICE_NOT_READY):
        cycle_count -= cycles
        if cycle_count <= 0:
            state = DEVICE_READY

