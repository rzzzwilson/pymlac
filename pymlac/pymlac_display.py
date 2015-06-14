#!/usr/bin/python 
# -*- coding: utf-8 -*-

"""
A display widget for the pymlac interpreter.
"""


import os
import sys
import traceback
import wx

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

    def Draw(self, dc):
        """Stub: called when the canvas needs to be re-drawn."""

        pass

    def Update(self):
        """Causes the canvas to be updated."""

        dc = wx.BufferedDC(wx.ClientDC(self), self.buffer)
        dc.BeginDrawing()
        dc.Clear()      # because maybe view size > map size
        self.Draw(dc)
        dc.EndDrawing()

    def OnPaint(self, event):
        """Paint the canvas to the screen."""

        # Blit the front buffer to the screen
        wx.BufferedPaintDC(self, self.buffer)

    def OnSize(self, event=None):
        """Create a new off-screen buffer to hold drawn data."""

        (width, height) = self.GetClientSizeTuple()
#        if width == 0:
#            width = 1
#        if height == 0:
#            height = 1

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

###############################################################################
# Define the events that are raised by the display widget.
###############################################################################

# display stop
_myEVT_DISPLAY_STOP = wx.NewEventType()
EVT_DISPLAY_STOP = wx.PyEventBinder(_myEVT_DISPLAY_STOP, 1)

class _DisplayEvent(wx.PyCommandEvent):
    """Event sent from the display widget."""

    def __init__(self, eventType, id):
        """Construct a display event.

        eventType  type of event
        id         unique event number

        Event will be adorned with attributes by raising code.
        """

        wx.PyCommandEvent.__init__(self, eventType, id)

###############################################################################
# The display widget proper
###############################################################################

class PymlacDisplay(_BufferedCanvas):
    """A widget to display pymlac draw lists."""

    # line colour
    DrawColour = '#ffff00'

    # panel background colour
    BackgroundColour = '#000000'

    # max coorcinates of pymlac display
    PymlacMaxX = 1024
    PymlaxMaxY = 1024

    def __init__(self, parent, **kwargs):
        """Initialise a display instance.

        parent       reference to parent object
        **kwargs     keyword args for Panel
        """

        # create and initialise the base panel
        _BufferedCanvas.__init__(self, parent=parent, **kwargs)
        self.SetBackgroundColour(PymlacDisplay.BackgroundColour)

        # set some internal state
        self.default_cursor = wx.CURSOR_DEFAULT
        self.drawlist = None        # list of (x1,y1,x2,y2)

        # set callback when parent resizes
#        self.onSizeCallback = self.ResizeCallback

        # force a resize, which sets up the rest of the state
        # eventually calls ResizeCallback()
        self.OnSize()

    ######
    # GUI stuff
    ######

    def OnKeyDown(self, event):
        pass

    def OnKeyUp(self, event):
        pass

    def OnLeftUp(self, event):
        """Left mouse button up.
        """

        pass

    def OnMiddleUp(self, event):
        """Middle mouse button up.  Do nothing in this version."""

        pass

    def OnRightUp(self, event):
        """Right mouse button up.

        Note that when we iterate through the layer_z_order list we must
        iterate on a *copy* as the user select process can modify
        self.layer_z_order.

        THIS CODE HASN'T BEEN LOOKED AT IN A LONG, LONG TIME.
        """

        pass

    def Draw(self, dc):
        """Do actual widget drawing.
        Overrides the _BufferedCanvas.draw() method.

        dc  device context to draw on

        Draws the current drawlist to the screen.
        """

        scaleX = self.view_width*1.0 / self.PymlacMaxX
        scaleY = self.view_height*1.0 / self.PymlaxMaxY
        dc.SetUserScale(min(scaleX,scaleY), min(scaleX,scaleY))

        if self.drawlist:
            dc.SetPen(wx.Pen(self.DrawColour))
            dc.DrawLineList(self.drawlist)

    ######
    # Change the drawlist
    ######

    def Drawlist(self, dl):
        self.drawlist = dl
        self.Update()

    ######
    # Routines for display events
    ######

    def RaiseEventStop(self):
        """Raise a display stop event."""

        event = _DisplayEvent(_myEVT_DISPLAY_STOP, self.GetId())
        self.GetEventHandler().ProcessEvent(event)

    def info(self, msg):
        """Display an information message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Information '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_INFORMATION)

    def warn(self, msg):
        """Display a warning message, log and graphically."""

        log_msg = '# ' + msg
        length = len(log_msg)
        prefix = '#### Warning '
        banner = prefix + '#'*(80 - len(log_msg) - len(prefix))
        log(banner)
        log(log_msg)
        log(banner)

        wx.MessageBox(msg, 'Warning', wx.OK | wx.ICON_ERROR)

