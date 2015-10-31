#!/usr/bin/python

"""
Emulate the imlac Paper Tape Reader/Punch (PTR/PTP).

We take some pains to closely emulate the *real* device, even
including misuse, such as no tape mounted.  This means we must tell
the PTR/PTP object how many CPU cycles have passed (tick()).
"""

import struct

from Globals import *


class PtrPtp(object):

    # number of chars per second we want
    PtrCharsPerSecond = 300
    PtpCharsPerSecond = 30

    # duty cycle for PTR is 30% ready and 70% not ready
    PtrReadyCycles = int((CYCLES_PER_SECOND / PtrCharsPerSecond) / 0.7) / 25
    PtrNotReadyCycles = int((CYCLES_PER_SECOND / PtrCharsPerSecond) / 0.3) / 25
    PtpNotReadyCycles = int(CYCLES_PER_SECOND / PtpCharsPerSecond)

    # no tape in reader, return 0377 (all holes see light)
    PtrEOF = 0377

    # module-level state variables
    device_use = None
    device_motor_on = False
    device_open_file = None
    device_filename = None
    device_cycle_count = 0
    device_ready = False

    ptr_at_eof = True
    ptr_value = PtrEOF

    # status values
    InUsePTR = 'PTR'
    InUsePTP = 'PTP'


    def __init__(self):
        """Initialize the papertape device."""

        self.reset()

    def reset(self):
        """Reset device to a known state."""

        # general device
        self.device_use = None
        self.device_motor_on = False
        self.device_open_file = None
        self.device_filename = None
        self.device_open_file = None
        self.device_filename = None
        self.device_ready = False

        # reader-specific
        self.ptr_at_eof = True
        self.ptr_value = self.PtrEOF

    def ready(self):
        """Test if device is ready."""

        return self.device_ready

    ###############
    # Interface routines for reader
    ###############

    def ptr_mount(self, fname):
        """Mount papertape file on the reader device."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("ptr_mount: Can't mount PTR file, being used as PTP")

        self.device_use = self.InUsePTR
        self.device_motor_on = False
        self.device_filename = fname
        self.device_open_file = open(self.device_filename, 'rb')
        self.device_ready = False
        self.device_cycle_count = self.PtrNotReadyCycles
        self.ptr_at_eof = False
        self.ptr_value = None

    def ptr_dismount(self):
        """Dismount a papertape file."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("ptr_dismount: Can't dismount PTR file, being used as PTP")

        self.device_use = None
        self.device_motor_on = False
        self.device_ready = False
        if self.device_filename:
            self.device_open_file.close()
            self.device_open_file = None
        self.device_filename = None
        self.ptr_at_eof = True
        self.ptr_value = self.PtrEOF

    def start(self):
        """Turn papertape reader motor on."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("start: Can't start PTR motor, being used as PTP")

        self.device_use = self.InUsePTR
        self.device_motor_on = True
        self.device_ready = False
        self.device_cycle_count = self.PtrReadyCycles

    def stop(self):
        """Stop reader motor."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("stop: Can't stop PTR motor, being used as PTP")

        self.device_motor_on = False
        self.device_ready = False
        self.device_cycle_count = self.PtrReadyCycles

    def read(self):
        """Read papertape value."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("ptr_read: Can't read PTR, being used as PTP")

        return self.ptr_value

    def ptr_eof(self):
        """Return reader EOF status."""

        if self.device_use == self.InUsePTP:
            raise RuntimeError("ptr_eof: Can't read PTR status, being used as PTP")

        return self.ptr_at_eof

    def ptr_tick(self, cycles):
        """Called to push PTR state along.

        cycles  number of cycles passed since last tick
        """

        if self.device_use != self.InUsePTR:
            return

        # if end of tape or motor off, do nothing, state remains unchanged
        if self.ptr_at_eof or not self.device_motor_on:
            return

        self.device_cycle_count -= cycles

        if self.device_cycle_count <= 0:
            if self.device_ready:
                self.device_ready = False
                self.device_cycle_count += self.PtrNotReadyCycles
            else:
                self.device_ready = True
                self.device_cycle_count += self.PtrReadyCycles
                self.ptr_value = self.device_open_file.read(1)
                if len(self.ptr_value) < 1:
                    # EOF on input file, pretend end of tape
                    self.ptr_at_eof = True
                    self.ptr_value = self.PtrEOF
                else:
                    self.ptr_value = ord(self.ptr_value)

    ###############
    # Interface routines for punch
    ###############

    def ptp_mount(self, fname):
        """Mount papertape file on the punch device."""

        # check usage of the device
        if self.device_use == self.InUsePTR:
            raise RuntimeError("ptp_mount: Can't mount PTP file, being used as PTR")

        self.device_use = self.InUsePTP
        self.device_motor_on = False
        self.device_ready = False
        self.device_cycle_count = self.PtrNotReadyCycles
        self.ptp_filename = fname
        self.device_open_file = open(self.ptp_filename, 'wb')
        self.ptp_at_eof = False
        self.ptp_value = None

    def ptp_dismount(self):
        """Dismount a papertape punch file."""

        if self.device_use == self.InUsePTR:
            raise RuntimeError("ptp_dismount: Can't dismount PTP file, being used as PTR")

        self.device_motor_on = False
        self.device_ready = False
        if self.ptp_filename:
            self.device_open_file.close()
            self.device_open_file = None
        self.ptp_filename = None
        self.ptp_at_eof = True
        self.ptp_value = self.PtrEOF

    def punch(self, value):
        """Write byte to papertape file.

        value  8 bit value to punch
        """

        if self.device_use == self.InUsePTR:
            raise RuntimeError("punch: Can't punch PTP file, being used as PTR")

        self.device_ready = False
        self.device_cycle_count = self.PtpNotReadyCycles
        self.device_open_file.write(struct.pack('1B', value))

    def ptp_tick(self, cycles):
        """Called to push PTP state along.

        cycles  number of cycles passed since last tick
        """

        if self.device_use != self.InUsePTP:
            return

        self.device_cycle_count -= cycles
        if self.device_cycle_count <= 0:
            self.device_ready = True
            self.device_cycle_count += self.PtrNotReadyCycles

