#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac keyboard emulation.

Usage: test_KBD.py [-h]
"""


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
        self.panel.SetSizer(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        self.display.Bind(wx.EVT_KEY_DOWN, self.OnKeyDown)
        self.display.Bind(wx.EVT_KEY_UP, self.OnKeyUp)

    def OnKeyDown(self, event):
        """Handle a "key down" event."""

        self.kbd.handle_down_event(event)

#        log('event=%s' % str(dir(event)))
#        self.display.AppendText('DOWN: Modifiers=%04x, GetKeyCode=%02x, UnicodeKey=%s\n'
#                                % (event.GetModifiers(),
#                                   event.GetKeyCode(),
#                                   str(event.GetUnicodeKey())))
#        self.display.Refresh()
#        if wx.WXK_LEFT == event.GetKeyCode():
#            print('LEFT key')

    def OnKeyUp(self, event):
        """Handle a "key up" event."""

        self.kbd.handle_up_event(event)

#        print('UP: Modifiers=%s, GetKeyCode=%s, UnicodeKey=%s'
#                % (str(event.GetModifiers()), str(event.GetKeyCode()), str(event.GetUnicodeKey())))

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

