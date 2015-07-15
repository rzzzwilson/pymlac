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


class TtyOut(object):

    def __init__(self):
        self.filename = None
        self.open_file = None
        self.cycle_count = 0
        self.state = DEVICE_NOT_READY

    def mount(self, fname):
        self.filename = fname
        self.open_file = open(self.filename, 'w')
        self.state = DEVICE_READY

    def dismount(self):
        if self.open_file:
            self.open_file.close()
        self.filename = None
        self.open_file = None
        self.state = DEVICE_NOT_READY

    def write(self, char):
        if self.open_file:
            self.open_file.write(char)
            self.cycle_count = DEVICE_NOT_READY_CYCLES

    def ready(self):
        return (self.state != DEVICE_NOT_READY)

    def clear(self):
        self.state = DEVICE_NOT_READY

    def tick(self, cycles):
        if (self.state == DEVICE_NOT_READY):
            self.cycle_count -= cycles
            if self.cycle_count <= 0:
                self.state = DEVICE_READY

