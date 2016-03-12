#!/usr/bin/python

"""
Emulate the Input TTY device (TTYIN).
"""

from Globals import *

import log
log = log.Log('test.log', log.Log.DEBUG)


class TtyIn(object):

    # define various internal states
    DEVICE_NOT_READY = 0
    DEVICE_READY = 1
    TTYIN_CHARS_PER_SECOND = 1000
#    DEVICE_READY_CYCLES = int(CYCLES_PER_SECOND / TTYIN_CHARS_PER_SECOND)
    DEVICE_READY_CYCLES = 200


    def __init__(self):
        """Initialize the TTYIN device."""

        self.filename = None
        self.open_file = None
        self.value = 0xff
        self.atEOF = True
        self.cycle_count = 0
        self.status = self.DEVICE_NOT_READY
        self.offset = 0

    def mount(self, fname):
        """Mount a file on the TTYIN device."""

        log("Mounting '%s' on TTYIN" % fname)

        self.filename = fname
        self.open_file = open(fname, 'r')
        self.value = self.open_file.read(1)
        self.atEOF = False
        self.cycle_count = self.DEVICE_READY_CYCLES
        self.status = self.DEVICE_NOT_READY
        if len(self.value) < 1:
            # EOF on input file
            self.atEOF = True
            self.cycle_count = 0
        else:
            self.value = ord(self.value)
        self.offset = 0

    def dismount(self):
        """Dismount the file on the TTYIN device."""

        log("Dismounting '%s' on TTYIN" % self.filename)

        if self.open_file:
            self.open_file.close()
        self.filename = None
        self.open_file = None
        self.value = 0
        self.atEOF = True
        self.status = self.DEVICE_NOT_READY
        self.offset = 0

    def read(self):
        """Return the current device value."""

        log("Reading TTYIN: returning %03o" % self.value)

        return self.value

    def ready(self):
        """Return device status."""

        return (self.status == self.DEVICE_READY)

    def clear(self):
        """Clear the device 'ready' status."""

        log("TTYIN: clearing flag")

        self.status = self.DEVICE_NOT_READY

    def tick(self, cycles):
        """Advance the device state by 'cycles' number of CPU cycles."""

        if not self.atEOF:
            self.cycle_count -= cycles
            if self.cycle_count <= 0:
                self.cycle_count += self.DEVICE_READY_CYCLES
                self.status = self.DEVICE_READY
                self.value = self.open_file.read(1)
                self.offset += 1
                if len(self.value) < 1:
                    # EOF on input file
                    self.atEOF = True
                    self.value = chr(0xff)
                    self.cycle_count = 0
                    self.status = self.DEVICE_NOT_READY
                self.value = ord(self.value)
