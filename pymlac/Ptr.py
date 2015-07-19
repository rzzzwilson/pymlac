#!/usr/bin/python

"""
Emulate the imlac Paper Tape Reader (PTR).

We take some pains to closely emulate the *real* PTR device, even
including misuse, such as no tape mounted.  This means we must tell
the PTR object how many CPU cycles have passed (tick()).
"""

from Globals import *


class Ptr(object):

    # number of chars per second we want
    CharsPerSecond = 300

    # duty cycle for PTR is 30% ready and 70% not ready
    ReadyCycles = int((CYCLES_PER_SECOND / CharsPerSecond) / 0.7) / 25
    NotReadyCycles = int((CYCLES_PER_SECOND / CharsPerSecond) / 0.3) / 25

    # no tape in reader, return 0377 (all holes see light)
    PtrEOF = 0377

    # module-level state variables
    motor_on = False
    device_ready = False
    open_file = None
    filename = None
    at_eof = True
    value = PtrEOF
    cycle_count = 0


    def __init__(self):
        """Initialize the paertape reader device."""

        self.motor_on = False
        self.device_ready = False
        self.open_file = None
        self.filename = None
        self.at_eof = True
        self.value = self.PtrEOF
        self.cycle_count = 0

    def mount(self, fname):
        """Mount papertape file on the reader device."""

        self.motor_on = False
        self.device_ready = False
        self.filename = fname
        self.open_file = open(self.filename, 'r')
        self.at_eof = False
        self.value = self.PtrEOF

    def dismount(self):
        """Dismount a papertape file."""

        self.motor_on = False
        self.device_ready = False
        if self.filename:
            self.open_file.close()
            self.open_file = None
        self.filename = None
        self.at_eof = True
        self.value = self.PtrEOF

    def start(self):
        """Turn papertape reader motor on."""

        self.motor_on = True
        self.device_ready = False
        self.cycle_count = self.ReadyCycles

    def stop(self):
        """Stop reader motor."""

        self.motor_on = False
        self.device_ready = False
        self.cycle_count = self.ReadyCycles

    def read(self):
        """Read papertape value."""

        print('Ptr: value=%04o' % self.value)
        return self.value

    def eof(self):
        """Return reader EOF status."""

        return self.at_eof

    def tick(self, cycles):
        """Called to push PTR state along.

        cycles  number of cycles passed since last tick
        """

        # if end of tape or motor off, do nothing, state remains unchanged
        if self.at_eof or not self.motor_on:
            return

        self.cycle_count -= cycles
        if self.cycle_count <= 0:
            if self.device_ready:
                self.device_ready = False
                self.cycle_count += self.NotReadyCycles
            else:
                self.device_ready = True
                self.cycle_count += self.ReadyCycles
                self.value = self.open_file.read(1)
                if len(self.value) < 1:
                    # EOF on input file, pretend end of tape
                    self.at_eof = True
                    self.value = self.PtrEOF
                else:
                    self.value = ord(self.value)

    def ready(self):
        """Test if reader is ready."""

        return self.device_ready

