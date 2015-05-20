#!/usr/bin/python 

"""
Emulate the imlac Paper Tape Reader (PTR).

We take some pains to closely emulate the *real* PTR device, even
including misuse, such as no tape mounted.  This means we must tell
the PTR object how many CPU cycles have passed (tick()).
"""

from Globals import *


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


def init():
    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    motor_on = False
    device_ready = False
    open_file = None
    filename = None
    at_eof = True
    value = PtrEOF
    cycle_count = 0

def mount(fname):
    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    motor_on = False
    device_ready = False
    filename = fname
    open_file = open(filename, 'r')
    at_eof = False
    value = PtrEOF

def dismount():
    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    motor_on = False
    device_ready = False
    if filename:
        open_file.close()
    filename = None
    at_eof = True
    value = PtrEOF

def start():
    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    motor_on = True
    device_ready = False
    cycle_count = NotReadyCycles

def stop():
    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    motor_on = False
    device_ready = False
    cycle_count = NotReadyCycles

def read():
    return value

def eof():
    return at_eof

def tick(cycles):
    """Called to push PTR state along.

    cycles  number of cycles passed since last tick
    """

    global motor_on, device_ready, filename, at_eof, value, cycle_count, open_file

    # if end of tape or motor off, do nothing, state remains unchanged
    if at_eof or not motor_on:
        return

    cycle_count -= cycles
    if cycle_count <= 0:
        if device_ready:
            device_ready = False
            cycle_count += NotReadyCycles
        else:
            device_ready = True
            cycle_count += ReadyCycles
            value = open_file.read(1)
            if len(value) < 1:
                # EOF on input file, pretend end of tape
                at_eof = True
                value = PtrEOF
            else:
                value = ord(value)

def ready():
    return device_ready

