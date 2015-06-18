#!/usr/bin/python 
# -*- coding: utf-8 -*-

"""
The Imlac display.
"""


import wx

from Globals import *
# if we don't have log.py, don't crash
try:
    import log
    log = log.Log('test.log', log.Log.DEBUG)
except ImportError:
    def log(*args, **kwargs):
        pass


# the widget version
__version__ = '0.0'

# type of events
DisplayStop = 1


######
# Base class for the widget canvas - buffered and flicker-free.
######

class _BufferedCanvas(wx.Panel):
    """Implements a buffered, flicker-free canvas widget.

    This class is based on:
        http://wiki.wxpython.org/index.cgi/BufferedCanvas
    """

    # The backing buffer
    buffer = None

    # max coordinates of scaled display                                          
    ScaleMaxX = 2048                                                            
    ScaleMaxY = 2048                                                            

    def __init__(self, parent, id=wx.ID_ANY, pos=wx.DefaultPosition,
                 size=wx.DefaultSize, style=wx.NO_FULL_REPAINT_ON_RESIZE):
        """Initialise the canvas.

        parent  reference to 'parent' widget
        id      the unique widget ID (NB: shadows builtin 'id')
        pos     canvas position
        size    canvas size
        style   wxPython style
        """

        wx.Panel.__init__(self, parent, id, pos, size, style)

        # Bind events
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

        # Disable background erasing (flicker-licious)
        def disable_event(*args, **kwargs):
            pass            # the sauce, please
        self.Bind(wx.EVT_ERASE_BACKGROUND, disable_event)

        # set callback upon onSize event
        self.onSizeCallback = None

        self.dc = None

    def Draw(self, dc):
        """Stub: called when the canvas needs to be re-drawn."""

        # set display scale
        scaleX = self.view_width*1.0 / self.ScaleMaxX
        scaleY = self.view_height*1.0 / self.ScaleMaxY
        dc.SetUserScale(min(scaleX,scaleY), min(scaleX,scaleY))

        # don't REPLACE this method, EXTEND it!

    def Update(self):
        """Causes the canvas to be updated."""

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.BeginDrawing()
        dc.Clear()      # because maybe view size > map size
        self.Draw(dc)
        dc.EndDrawing()
        self.dc = dc

    def OnPaint(self, event):
        """Paint the canvas to the screen."""

        # Blit the front buffer to the screen
        wx.BufferedPaintDC(self, self.buffer)

    def OnSize(self, event=None):
        """Create a new off-screen buffer to hold drawn data."""

        (width, height) = self.GetClientSizeTuple()

        minsize = min(width, height)
        self.SetSize((minsize, minsize))

        self.view_width = minsize
        self.view_height = minsize

        # new off-screen buffer
        self.buffer = wx.EmptyBitmap(minsize, minsize)

        # call onSize callback, if registered
        if self.onSizeCallback:
            self.onSizeCallback()

        # Now update the screen
        self.Update()


################################################################################
# The actual pymlc display widget.
################################################################################

class Display(_BufferedCanvas):

    BackgroundColour = 'black'
    DrawColour = '#ffff88'

    SYNC_HZ = 40
    SYNC_40HZ_CYCLE_COUNT = int(CYCLES_PER_SECOND / SYNC_HZ)

    # max coorcinates of pymlac display                                          
    ScaleMaxX = 2048                                                            
    ScaleMaxY = 2048                                                            


    def __init__(self, parent, **kwargs):
        # create and initialise the base panel                                   
        _BufferedCanvas.__init__(self, parent=parent, **kwargs)                  
        self.SetBackgroundColour(self.BackgroundColour)                        
                                                                                                         
        # set internal state
        self.running = 0
        self.cycle_count = 0
        self.Sync40hz = 1
        self.drawlist = []

        self.OnSize()

    def draw(self, sd, x1, y1, x2, y2):
        """Draw a line on the screen.

        sd      True if solid line, False if dotted
        x1, y1  start coordinates
        x2, y2  end coordinates
        """

        self.drawlist.append((sd, x1, y1, x2, y2))
        self.Update()

    def Draw(self, dc):
        """Update the display on the widget screen."""

        # there's some code in super.Draw() we need
        super(Display, self).Draw(dc)

        pen = wx.Pen(self.DrawColour)

        for (sd, x1, y1, x2, y2) in self.drawlist:
            if sd:
                pen.SetStyle(wx.SOLID)
                pen.SetWidth(2)
            else:
                pen.SetStyle(wx.DOT)
                pen.SetWidth(3)
            dc.SetPen(pen)
        
            dc.DrawLine(x1, y1, x2, y2)

    def syncclear(self):
        self.Sync40hz = 0
        self.cycle_count = self.SYNC_40HZ_CYCLE_COUNT

    @property
    def ready(self):
        return self.Sync40hz

    def tick(self, cycles):
        """Advance the internal state by given cycles."""

        self.cycle_count -= cycles
        if self.cycle_count <= 0:
            self.Sync40hz = 1
            self.cycle_count = 0

