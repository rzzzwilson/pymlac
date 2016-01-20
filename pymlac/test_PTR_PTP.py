#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac papertape reader code.

Usage: test_PTR_PTP.py <options>

where <options> is zero or more of:
          -h    print this help and stop
"""

# We exercise the papertape reader module by:
#   1. manipulating the device to test error conditions
#   2. writing test *.ptp files which we mount and read


import os

import PtrPtp


# module global constants
PtrFilename = '_#PTR#_.ptp'
PtpFilename = '_#PTP#_.ptp'

Logfile = 'test_PTR_PTP.log'


def logger(*args):
    msg = ' '.join(args)
    with open(Logfile, 'ab') as fd:
        fd.write(msg + '\n')

def read_no_tape(ptr):
    """Read from device with no tape mounted."""

    # read before turning on
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.ptr_tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')

    # turn device on, still no tape
    ptr.start()
    ptr.ptr_tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.ptr_tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.stop()
    ptr.ptr_dismount()

def create_papertape(filename):
    """Create a PTP file."""

    # create a test papertape
    with open(filename, 'wb') as fd:
        # leader
        for _ in range(128):
            fd.write(chr(0))

        for v in range(1, 256):
            fd.write(chr(v))

        # trailer
        for _ in range(128):
            fd.write(chr(0))

def create_papertape_ptp(ptp, filename):
    """Create a PTP file using the Ptp device."""

#    ptp.reset()
    ptp.ptp_mount(filename)

    # leader
    for _ in range(128):
        while not ptp.ready():
            ptp.ptp_tick(1)
        ptp.punch(0)
        while ptp.ready():
            ptp.ptp_tick(1)

    # body
    for v in range(1, 256):
        while not ptp.ready():
            ptp.ptp_tick(1)
        ptp.punch(v)

    # trailer
    for _ in range(128):
        while not ptp.ready():
            ptp.ptp_tick(1)
        ptp.punch(0)

#    ptp.stop()
    ptp.ptp_dismount()

def read_tape(ptr, filename):
    """Create tape and read it."""

    # now mount and read tape
#    ptr.reset()
    ptr.ptr_mount(filename)
    ptr.start()

    # read leader
    byte = None
    count = 0
    while True:
        while not ptr.ready():
            ptr.ptr_tick(1)
        byte = ptr.read()
        while ptr.ready():
            ptr.ptr_tick(1)
        if byte != 0:
            break
        count += 1

    print('%d bytes of leader' % count)

    # read body, already read first byte
    byte = None
    count = 1
    while True:
        while not ptr.ready():
            ptr.ptr_tick(1)
        byte = ptr.read()
        while ptr.ready():
            ptr.ptr_tick(1)
        if byte == 0:
            break
        count += 1

    print('%d bytes of body' % count)

    # read trailer, already read first byte
    byte = None
    count = 1
    while True:
        while not ptr.ready():
            ptr.ptr_tick(1)
        byte = ptr.read()
        if byte != 0:
            break
        count += 1
        while ptr.ready():
            ptr.ptr_tick(1)

    ptr.stop()

    print('%d bytes of trailer' % count)

    ptr.ptr_dismount()

def main():
    """Test the papertape reader."""

    try:
        os.remove(Logfile)
    except OSError:
        pass        # ignore 'file not there'

    ptrptp = PtrPtp.PtrPtp()
    logger('created reader/punch device')

    read_no_tape(ptrptp)
    create_papertape(PtrFilename)
    read_tape(ptrptp, PtrFilename)
    create_papertape_ptp(ptrptp, PtpFilename)
    read_tape(ptrptp, PtpFilename)



################################################################################

if __name__ == '__main__':
    main()

