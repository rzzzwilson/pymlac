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


import Ptr
import Ptp


# module global constants
PtrFilename = '_#PTR#_.ptp'
PtpFilename = '_#PTP#_.ptp'


def read_no_tape(ptr):
    """Read from device with no tape mounted."""

    # read before turning on
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')

    # turn device on, still no tape
    ptr.start()
    ptr.tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.tick(1000000)     # wait a long time
    byte = ptr.read()
    if byte != 0377:
        print('Error')
    ptr.stop()

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

    ptp.mount(filename)
    ptp.start()

    # leader
    for _ in range(128):
        while not ptp.ready():
            ptp.tick(1)
        ptp.write(chr(0))
        while ptp.ready():
            ptp.tick(1)

    # body
    for v in range(1, 256):
        while not ptp.ready():
            ptp.tick(1)
        ptp.write(chr(v))
        while ptp.ready():
            ptp.tick(1)

    # trailer
    for _ in range(128):
        while not ptp.ready():
            ptp.tick(1)
        ptp.write(chr(0))
        while ptp.ready():
            ptp.tick(1)

    ptp.stop()
    ptp.dismount()

def read_tape(ptr, filename):
    """Create tape and read it."""

    # now mount and read tape
    ptr.mount(filename)
    ptr.start()

    # read leader
    byte = None
    count = 0
    while True:
        while not ptr.ready():
            ptr.tick(1)
        byte = ptr.read()
        while ptr.ready():                                                   
            ptr.tick(1)
        if byte != 0:
            break
        count += 1

    print('%d bytes of leader' % count)

    # read body, already read first byte
    byte = None
    count = 1
    while True:
        while not ptr.ready():
            ptr.tick(1)
        byte = ptr.read()
        while ptr.ready():                                                   
            ptr.tick(1)
        if byte == 0:
            break
        count += 1

    print('%d bytes of body' % count)

    # read trailer, already read first byte
    byte = None
    count = 1
    while True:
        while not ptr.ready():
            ptr.tick(1)
        byte = ptr.read()
        if byte != 0:
            break
        count += 1
        while ptr.ready():                                                   
            ptr.tick(1)

    ptr.stop()

    print('%d bytes of trailer' % count)

def main():
    """Test the papertape reader."""

    ptr = Ptr.Ptr()
    ptp = Ptp.Ptp()

    read_no_tape(ptr)
    create_papertape(PtrFilename)
    read_tape(ptr, PtrFilename)
    create_papertape_ptp(ptp, PtpFilename)
    read_tape(ptr, PtpFilename)



################################################################################

if __name__ == '__main__':
    main()

