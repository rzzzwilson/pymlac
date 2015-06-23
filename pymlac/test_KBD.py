#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac keyboard code.

Usage: test_KBD.py <options>

where <options> is zero or more of:
          -h    print this help and stop
"""


import Kbd


def main():
    """Test the keyboard device."""

    kbd = Kbd.Kbd()


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
    main()
    
