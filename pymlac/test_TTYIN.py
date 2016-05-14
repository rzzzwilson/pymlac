#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac TTY input device.

Usage: test_TTYIN.py <options>

where <options> is zero or more of:
          -h    print this help and stop
"""


import TtyIn


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
    ttyin = TtyIn.TtyIn()

    # read without mounting
    val = ttyin.read()
    expected = 0377
    if val != expected:
        error('No mounted file: read() returned %d, expected %d' % (val, expected))

    # dismount
    ttyin.dismount()

def mount_dismount(filename):
    """Just mount then dismount file."""

    ttyin = TtyIn.TtyIn()
    ttyin.mount(filename)
    ttyin.dismount()

def read_tty(filename):
    """Mount a file and read from it."""

    ttyin = TtyIn.TtyIn()
    ttyin.mount(filename)

    # read leader
    byte = None
    count = 1
    while True:
        while not ttyin.ready():
            ttyin.tick(1)
        byte = ttyin.read()
        ttyin.clear()
        if byte != 0:
            break
        count += 1

    print('%d bytes of leader' % count)

    # read body, already read first byte
    count = 1
    while count < 32:
        while not ttyin.ready():
            ttyin.tick(1)
        byte = ttyin.read()
        ttyin.clear()
        count += 1

    print('%d bytes of body' % count)

    # now dismount the file
    ttyin.dismount()

def main():
    """Test the keyboard device."""

    # test device with no mounted file
    no_mounted_file()

    # create a test file
    create_tty_file(TtyFilename)

    # test reading from mounted device
    read_tty(TtyFilename)

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

