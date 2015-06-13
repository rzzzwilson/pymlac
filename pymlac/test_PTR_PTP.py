#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac papertape reader code.

Usage: test_PTR_PTP.py <options>

where <filename> is a papertape file (*.ptp)
  and <options> is zero or more of:
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


def read_no_tape():
    """Read from device with no tape mounted."""

    # read before turning on
    byte = Ptr.read()
    if byte != 0377:
        print('Error')
    Ptr.tick(1000000)     # wait a long time
    byte = Ptr.read()
    if byte != 0377:
        print('Error')

    # turn device on, still no tape
    Ptr.start()
    Ptr.tick(1000000)     # wait a long time
    byte = Ptr.read()
    if byte != 0377:
        print('Error')
    Ptr.tick(1000000)     # wait a long time
    byte = Ptr.read()
    if byte != 0377:
        print('Error')
    Ptr.stop()

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

def create_papertape_ptp(filename):
    """Create a PTP file using the Ptp device."""

    Ptp.mount(filename)
    Ptp.start()

    # leader
    for _ in range(128):
        while not Ptp.ready():
            Ptp.tick(1)
        Ptp.write(chr(0))
        while Ptp.ready():
            Ptp.tick(1)

    # body
    for v in range(1, 256):
        while not Ptp.ready():
            Ptp.tick(1)
        Ptp.write(chr(v))
        while Ptp.ready():
            Ptp.tick(1)

    # trailer
    for _ in range(128):
        while not Ptp.ready():
            Ptp.tick(1)
        Ptp.write(chr(0))
        while Ptp.ready():
            Ptp.tick(1)

    Ptp.stop()
    Ptp.dismount()

def read_tape(filename):
    """Create tape and read it."""

    # now mount and read tape
    Ptr.mount(filename)
    Ptr.start()

    # read leader
    byte = None
    count = 0
    while True:
        while not Ptr.ready():
            Ptr.tick(1)
        byte = Ptr.read()
        while Ptr.ready():                                                   
            Ptr.tick(1)
        if byte != 0:
            break
        count += 1

    print('%d bytes of leader' % count)

    # read body, already read first byte
    byte = None
    count = 1
    while True:
        while not Ptr.ready():
            Ptr.tick(1)
        byte = Ptr.read()
        while Ptr.ready():                                                   
            Ptr.tick(1)
        if byte == 0:
            break
        count += 1

    print('%d bytes of body' % count)

    # read trailer, already read first byte
    byte = None
    count = 1
    while True:
        while not Ptr.ready():
            Ptr.tick(1)
        byte = Ptr.read()
        if byte != 0:
            break
        count += 1
        while Ptr.ready():                                                   
            Ptr.tick(1)

    Ptr.stop()

    print('%d bytes of trailer' % count)

def main():
    """Test the papertape reader."""

    Ptr.init()
    Ptp.init()

    read_no_tape()
    create_papertape(PtrFilename)
    read_tape(PtrFilename)
    create_papertape_ptp(PtpFilename)
    read_tape(PtpFilename)



################################################################################

if __name__ == '__main__':
    main()

