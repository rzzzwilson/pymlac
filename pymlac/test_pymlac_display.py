#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test the pymlac display widget.

Usage: test_pymlac_display.py [-h]
"""


import wx
import pymlac_display as Display

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
        self.display = Display.PymlacDisplay(self.panel)
        box.Add(self.display, proportion=1, border=1, flag=wx.EXPAND)
        self.panel.SetSizer(box)
        self.panel.Layout()
        self.Centre()
        self.Show(True)

        self.Bind(wx.EVT_SIZE, self.OnSize)

        self.lock = False

        self.Refresh()

        self.display.Drawlist([(0,0,1023,1023), (1023,0,0,1023)])

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

#########


def init(run_address, tracefile, tstart, tend, boot_rom=None, corefile=None):
    global tracestart, traceend

    Memory.init(boot_rom, corefile)
    Trace.init(tracefile)
    tracestart = tstart
    traceend = tend
    DisplayCPU.init()
    MainCPU.init()

def close(corefile=None):
    if corefile:
        Memory.savecore(corefile)
    sys.exit()

def set_ROM(type):
    Memory.set_ROM(type)

def set_boot(romtype):
    pass

def __tick_all(cycles):
    Ptr.tick(cycles)
    Ptp.tick(cycles)
    TtyIn.tick(cycles)
    TtyOut.tick(cycles)

def set_trace(tstart, tend=None):
    """Set trace to required range of values."""

    global tracestart, traceend

    if tstart:
        tracestart = tstart
        traceend = tend
        Trace.tracing = True
    else:
        Trace.tracing = False

def execute_once():
    if traceend is None:
        if MainCPU.PC == tracestart:
            Trace.settrace(True)
    else:
        Trace.settrace(MainCPU.PC >= tracestart and MainCPU.PC <= traceend)

    if DisplayCPU.ison():
        Trace.trace('%6.6o' % DisplayCPU.DPC)
    Trace.trace('\t')

    instruction_cycles = DisplayCPU.execute_one_instruction()

    Trace.trace('%6.6o\t' % MainCPU.PC)

    instruction_cycles += MainCPU.execute_one_instruction()

    Trace.itraceend(DisplayCPU.ison())

    __tick_all(instruction_cycles)

    if not DisplayCPU.ison() and not MainCPU.running:
        return 0

    return instruction_cycles

def run():
    """Start the machine and run until it halts."""

    MainCPU.running = True

    while execute_once() > 0:
        pass

    MainCPU.running = False

