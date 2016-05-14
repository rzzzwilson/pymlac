#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac TTY output device.

Usage: test_TTYOUT.py <options>

where <options> is zero or more of:
          -h    print this help and stop
"""


import TtyOut


# count of errors found
ErrorCount = 0

# module global constants
TtyFilename = '_#TTY#_.ptp'


def error(msg):
    global ErrorCount

    ErrorCount += 1

    print(msg)

def create_tty_file(filename):
    """Create a TTY file."""

    # create a test file
    with open(filename, 'wb') as fd:
        # leader
        for _ in range(16):
            fd.write(chr(0))

        for v in range(1, 33):
            fd.write(chr(v))

def no_mounted_file():
    ttyout = TtyOut.TtyOut()

    # write without mounting
    val = ttyout.write(0)

    # dismount
    ttyout.dismount()

def mount_dismount(filename):
    """Just mount then dismount file."""

    print('mount_dismount: filename=%s' % str(filename))
    ttyout = TtyOut.TtyOut()
    ttyout.mount(filename)
    ttyout.dismount()

def write_tty(filename):
    """Mount a file and write to it."""

    ttyout = TtyOut.TtyOut()
    ttyout.mount(filename)

    # write leader
    count = 0
    while count < 16:
        while not ttyout.ready():
            ttyout.tick(1)
        #byte = ttyout.write(chr(0))
        byte = ttyout.write(0)
        ttyout.clear()
        count += 1

    print('wrote %d bytes of leader' % count)

    # write body
    count = 0
    while count < 32:
        while not ttyout.ready():
            ttyout.tick(1)
        #ttyout.write(chr(1))
        ttyout.write(1)
        ttyout.clear()
        count += 1

    print('%d bytes of body' % count)

    # now dismount the file
    ttyout.dismount()

def main():
    """Test the TTY out device."""

    # test device with no mounted file
    no_mounted_file()

    # just mount, then dismount
    mount_dismount(TtyFilename)

    # test reading from mounted device
    write_tty(TtyFilename)

    # print number of errors
    print('\n***** %d errors' % ErrorCount)

#    return ErrorCount
    return 0


################################################################################

if __name__ == '__main__':
    import sys
    import getopt

    def usage(msg=None):
        if msg:
            print('*'*60)
            print(msg)
            print('*'*60)
        print(__doc__)

    # handle command line options
    try:
        (opts, args) = getopt.gnu_getopt(sys.argv, "h", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(10)

    for (opt, arg) in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    # we should have NO parameters
    if len(args) != 1:
        bad_args = ''
        for a in args[1:]:
            bad_args += ' ' + str(a)
        usage('Unrecognized param(s): %s' % bad_args)
        sys.exit(10)

    # run the tests
    sys.exit(main())

