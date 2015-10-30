#!/usr/bin/python

"""
Emulate the Paper Tape Punch (PTP).
"""


from Globals import *


class Ptp(object):

    # define various internal states
    MOTOR_ON = 1
    MOTOR_OFF = 0
    DEVICE_NOT_READY = 0
    DEVICE_READY = 1
    PTP_CHARS_PER_SECOND = 30
    DEVICE_NOT_READY_CYCLES = int(CYCLES_PER_SECOND / PTP_CHARS_PER_SECOND)

    # module-level state variables
    motor_state = MOTOR_OFF
    device_state = DEVICE_NOT_READY
    filename = None
    open_file = None
    cycle_count = None


    def init(self):
        """Initialize the punch."""

        self.motor_state = self.MOTOR_OFF
        self.device_state = self.DEVICE_NOT_READY
        self.filename = None
        self.open_file = None

    def mount(self, ptp_filename):
        """Mount a file on the punch."""

        self.motor_state = self.MOTOR_OFF
        self.device_state = self.DEVICE_NOT_READY
        self.filename = ptp_filename
        self.open_file = open(self.filename, 'w')

    def dismount(self):
        """Dismount the file from the punch."""

        self.motor_state = self.MOTOR_OFF
        self.device_state = self.DEVICE_NOT_READY
        if self.open_file:
            self.open_file.close()
        self.filename = None
        self.open_file = None

    def start(self):
        """Start the punch motor."""

        self.motor_state = self.MOTOR_ON
        self.device_state = self.DEVICE_NOT_READY
        self.cycle_count = self.DEVICE_NOT_READY_CYCLES

    def stop(self):
        """Stop the punch motor."""

        self.motor_state = self.MOTOR_OFF
        self.device_state = self.DEVICE_NOT_READY

    def write(self, ch):
        """Punch an 8 bit value to the tape file."""

        print('PTP.write: ch=%s (%d)' % (type(ch), ch))

        self.device_state = self.DEVICE_NOT_READY
        self.cycle_count = self.DEVICE_NOT_READY_CYCLES
        self.open_file.write(str(ch))

    def tick(self, cycles):
        """Move the state of the punch along."""

        print('PTP: tick() called, cycles=%s, self.cycle_count=%s' % (str(cycles), str(self.cycle_count)))

        if self.motor_state == self.MOTOR_OFF or not self.open_file:
            self.device_state = self.DEVICE_NOT_READY
            return

        self.cycle_count -= cycles
        if self.cycle_count <= 0:
            self.device_state = self.DEVICE_READY

    def ready(self):
        """Get the punch state."""

        return self.device_state == self.DEVICE_READY

