"""
Test the pymlac display widget.

Usage: test_Display.py [-h]
"""


import Display

# if we don't have log.py, don't crash
try:
    import log
    log = log.Log('test.log', log.Log.DEBUG)
except ImportError:
    def log(*args, **kwargs):
        pass


def test():
    display = Display.Display()
    display.draw(0, 0, 1023, 1023)
    display.draw(1023, 0, 0, 1023)
    display.draw(512, 0, 1023, 512)
    display.draw(1023, 512, 512, 1023)
    display.draw(512, 1023, 0, 512)
    display.draw(0, 512, 512, 0)
    for x in (0, 256, 512, 768, 1023):
        display.draw(x, 0, x, 1023, dotted=True)

    for y in (0, 256, 512, 768, 1023):
        display.draw(0, y, 1023, y, dotted=True)

    display.close()


################################################################################

if __name__ == '__main__':
    import sys
    import getopt
    import traceback

    # print some usage information
    def usage(msg=None):
        if msg:
            print(msg+'\n')
        print(__doc__)        # module docstring used

    # our own handler for uncaught exceptions
    def excepthook(type, value, tb):
        msg = '\n' + '=' * 80
        msg += '\nUncaught exception:\n'
        msg += ''.join(traceback.format_exception(type, value, tb))
        msg += '=' * 80 + '\n'
        print(msg)
        sys.exit(1)

    # plug our handler into the python system
    sys.excepthook = excepthook

    # decide which tiles to use, default is GMT
    argv = sys.argv[1:]

    try:
        (opts, args) = getopt.getopt(argv, 'h', ['help'])
    except getopt.error:
        usage()
        sys.exit(1)

    for (opt, param) in opts:
        if opt in ['-h', '--help']:
            usage()
            sys.exit(0)

    test()

#    # start wxPython app
#    app = wx.App()
#    TestFrame().Show()
#    app.MainLoop()
#    sys.exit(0)
#
