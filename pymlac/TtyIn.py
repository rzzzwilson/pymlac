#!/usr/bin/python

"""
Emulate the Input TTY device (TTYIN).
"""

from Globals import *

import log
log = log.Log('test_TTYIN.log', log.Log.DEBUG)


class TtyIn(object):

    # define various internal states
    DEVICE_NOT_READY = 0
    DEVICE_READY = 1
    TTYIN_CHARS_PER_SECOND = 1000
#    DEVICE_READY_CYCLES = int(CYCLES_PER_SECOND / TTYIN_CHARS_PER_SECOND)
    DEVICE_READY_CYCLES = 200


    def __init__(self):
        """Initialize the TTYIN device."""

        log('TTYIN: Initializing device')

        self.filename = None
        self.open_file = None
        self.value = 0
        self.atEOF = True
        self.cycle_count = 0
        self.status = self.DEVICE_NOT_READY

        log('TTYIN: DEVICE_READY_CYCLES=%d' % self.DEVICE_READY_CYCLES)

    def mount(self, fname):
        """Mount a file on the TTYIN device."""

        log('TTYIN: Mounting file %s on device' % fname)

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
            self.value = 0
            log('TTYIN: EOF set on device (file %s)' % self.fname)
        self.value = ord(self.value)
        self.offset = -1

    def dismount(self):
        """Dismount the file on the TTYIN device."""

        log('TTYIN: Dismounting file %s' % self.filename)

        if self.open_file:
            self.open_file.close()
        self.filename = None
        self.open_file = None
        self.value = 0
        self.atEOF = True
        self.status = self.DEVICE_NOT_READY
        self.offset = None

    def read(self):
        """Return the current device value."""

        log('TTYIN: Reading device, value is %03o, offset=%04o' % (self.value, self.offset))

        return self.value

    def ready(self):
        """Return device status."""

        log("TTYIN: Device 'ready' status is %s, offset=%d"
            % (str(self.status == self.DEVICE_READY), self.offset))

        return (self.status == self.DEVICE_READY)

    def clear(self):
        """Clear the device 'ready' status."""

        log("TTYIN: Clearing device 'ready' status")

        self.status = self.DEVICE_NOT_READY

    def tick(self, cycles):
        """Advance the device state by 'cycles' number of CPU cycles."""

        if not self.atEOF:
            log("TTYIN: Doing 'tick' cycle=%d, .atEOF=%s, .cycle_count=%d"
                    % (cycles, str(self.atEOF), self.cycle_count))
            self.cycle_count -= cycles
            if self.cycle_count <= 0:
                self.cycle_count += self.DEVICE_READY_CYCLES
                self.status = self.DEVICE_READY
                self.value = self.open_file.read(1)
                if len(self.value) < 1:
                    # EOF on input file
                    self.atEOF = True
                    self.value = chr(0)
                    self.cycle_count = 0
                    self.status = self.DEVICE_NOT_READY
                    log('TTYIN: EOF set on device (file %s)' % self.filename)
                else:
                    log('TTYIN: .cycle_count expired, new character is %s (%03o)'
                            % (self.value, ord(self.value[0])))
                self.value = ord(self.value)
                self.offset += 1
