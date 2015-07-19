#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac display widget.

Usage: test_Display.py [-h]
"""


import wx
import Display

# if we don't have log.py, don't crash                                           
try:                                                                             
    import log                                                     
    log = log.Log('test.log', log.Log.DEBUG)                                     
except ImportError:                                                              
    def log(*args, **kwargs):                                                    
        pass                                                                     


######
# Various demo constants
######

WindowTitleHeight = 22
DefaultAppSize = (600, 600+WindowTitleHeight)

################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('Test pymlac display - %s'
                                 % Display.__version__))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.ClearBackground()

        # build the GUI
        box = wx.BoxSizer(wx.VERTICAL)
        self.display = Display.Display(self.panel)
        box.Add(self.display, proportion=1, border=1, flag=wx.EXPAND)
        self.panel.SetSizer(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.lock = False

        self.Refresh()

        self.display.draw(0, 0, 2047, 2047)
        self.display.draw(2047, 0, 0, 2047, dotted=True)

    def OnSize(self, event):
        """Maintain square window."""

        if not self.lock:
            self.lock = True
            (w, h) = event.GetSize()
            size = min(w, h)
            self.SetSize((size-WindowTitleHeight, size))
            self.lock = False

        event.Skip()

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
        print msg
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

    # start wxPython app
    app = wx.App()
    TestFrame().Show()
    app.MainLoop()
    sys.exit(0)

