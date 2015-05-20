#!/usr/bin/python 

"""
Emulate the Paper Tape Punch (PTP).
"""


from Globals import *


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


def init():
    global motor_state, device_state, filename, open_file

    motor_state = MOTOR_OFF
    device_state = DEVICE_NOT_READY
    filename = None
    open_file = None

def mount(ptp_filename):
    global motor_state, device_state, filename, open_file

    motor_state = MOTOR_OFF
    device_state = DEVICE_NOT_READY
    filename = ptp_filename
    open_file = open(filename, 'w')

def dismount():
    global motor_state, device_state, filename, open_file

    motor_state = MOTOR_OFF
    device_state = DEVICE_NOT_READY
    if open_file:
        open_file.close()
    filename = None
    open_file = None

def start():
    global motor_state, device_state, filename, open_file

    motor_state = MOTOR_ON
    device_state = DEVICE_NOT_READY
    cycle_count = DEVICE_NOT_READY_CYCLES

def stop():
    global motor_state, device_state, filename, open_file

    motor_state = MOTOR_OFF
    device_state = DEVICE_NOT_READY

def write(ch):
    global motor_state, device_state, filename, open_file

    device_state = DEVICE_NOT_READY
    cycle_count = DEVICE_NOT_READY_CYCLES
    open_file.write(ch)

def tick(cycles):
    global motor_state, device_state, filename, open_file

    if motor_state == MOTOR_OFF or not open_file:
        device_state = DEVICE_NOT_READY
        return

    cycle_count -= cycles
    if cycle_count <= 0:
        device_state = DEVICE_READY

def ready():
    return device_state == DEVICE_READY

