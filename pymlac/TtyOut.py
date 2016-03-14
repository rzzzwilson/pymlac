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

import log
log = log.Log('test.log', log.Log.DEBUG)


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
        log('TTYOUT: writing byte %03o, .open_file=%s' % (char, self.open_file))
        if self.open_file:
            self.open_file.write(chr(char))
            self.state = DEVICE_NOT_READY
            self.cycle_count = DEVICE_NOT_READY_CYCLES
            log('TTYOUT: device -> DEVICE_NOT_READY, .cycle_count=%d' % self.cycle_count)

    def ready(self):
        return (self.state != DEVICE_NOT_READY)

    def clear(self):
        self.state = DEVICE_READY

    def tick(self, cycles):
        if (self.state == DEVICE_NOT_READY):
            self.cycle_count -= cycles
            log('TTYOUT: tick: .cycle_count set to %d' % self.cycle_count)
            if self.cycle_count <= 0:
                log('TTYOUT: tick: device set to DEVICE_READY')
                self.state = DEVICE_READY

