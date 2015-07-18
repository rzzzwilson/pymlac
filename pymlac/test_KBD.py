#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac keyboard emulation.

Usage: test_KBD.py [-h]
"""


import string
import wx
import Kbd

# if we don't have log.py, don't crash                                           
try:                                                                             
    import log                                                     
    log = log.Log('test_KBD.log', log.Log.DEBUG)                                     
except ImportError:                                                              
    def log(*args, **kwargs):                                                    
        pass                                                                     


######
# Various demo constants
######

WindowTitleHeight = 22
DefaultAppSize = (400, 200+WindowTitleHeight)

################################################################################
# The main application frame
################################################################################

class TestFrame(wx.Frame):
    def __init__(self):
        wx.Frame.__init__(self, None, size=DefaultAppSize,
                          title=('Test pymlac KBD'))
        self.SetMinSize(DefaultAppSize)
        self.panel = wx.Panel(self, wx.ID_ANY)
        self.panel.ClearBackground()

        # instantiate the keyboard device
        self.kbd = Kbd.Kbd()

        # build the GUI
        box = wx.BoxSizer(wx.VERTICAL)

        self.display = wx.TextCtrl(self.panel)
        box.Add(self.display, proportion=1, border=1, flag=wx.EXPAND)

        btnSizer = wx.BoxSizer(wx.HORIZONTAL)
        clearBtn = wx.Button(self.panel, wx.ID_ANY, 'Clear')
        readBtn = wx.Button(self.panel, wx.ID_ANY, 'Read')
        btnSizer.Add(clearBtn, 0, wx.ALL, 5)
        btnSizer.Add(readBtn, 0, wx.ALL, 5)
        box.Add(btnSizer, 0, wx.ALL, 5)

        self.panel.SetSizer(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        self.display.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.display.Bind(wx.EVT_KEY_UP, self.OnKeyUp)
        self.display.Bind(wx.EVT_CHAR, self.OnChar)

        clearBtn.Bind(wx.EVT_BUTTON, self.onClear)
        readBtn.Bind(wx.EVT_BUTTON, self.onRead)

    def onClear(self, event):
        """Handle a CLEAR operation."""

        self.kbd.clear()

    def onRead(self, event):
        """Handle a READ operation."""

        value = self.kbd.read()
        char = value & 0xff
        char_str = chr(char)
        if char_str not in string.printable:
            char_str = '<unprintable>'
        R = (value >> 10) & 0x01
        C = (value >> 9) & 0x01
        S = (value >> 8) & 0x01

        self.display.AppendText('R=%d, C=%d, S=%d, char=%04o (%s)\n'
                                % (R, C, S, char, char_str))
        self.display.Refresh()


    def OnKeyDown(self, event):
        """Handle a "key down" event."""

#        self.display.AppendText('DOWN: Modifiers=%04x, GetKeyCode=%04x\n'
#                                % (event.GetModifiers(), event.GetKeyCode()))
#        self.display.Refresh()

        self.kbd.handle_down_event(event)

    def OnKeyUp(self, event):
        """Handle a "key up" event."""

#        self.display.AppendText('UP: Modifiers=%04x, GetKeyCode=%04x\n'
#                                % (event.GetModifiers(), event.GetKeyCode()))
#        self.display.Refresh()

        self.kbd.handle_up_event(event)

    def OnChar(self, event):
        """Handle a "char" event."""

        print('CHAR: Modifiers=%04x, GetKeyCode=%04x'
              % (event.GetModifiers(), event.GetKeyCode()))

        self.kbd.handle_char_event(event)

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

