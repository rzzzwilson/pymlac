#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The 'led16' widget.

Event attributes:
    'state' - the current displayed value (int)

Instance methods:
    Led16(parent, label, pos, led_on, led_off, *args, **kwargs)
        parent      owning widget
        label       label above leftmost led
        pos         position (x, y)
        led_on      image of led 'on' state
        led_off     image of led 'off' state
        args        ?
        kwargs      ?
    SetState(state)
        sets widget state, 'state' is a 16 bit value.

The widget will look like:

              +-----------------------------------+
              |             <TopSpacer>           |
<LeftSpacer>--> O O O O O O O O O O O O O O O O  <---<RightSpacer>
              | +-+-----+-----+-----+-----+-----+ |
              |             <BotSpacer>           |
              +-----------------------------------+
"""

import os
import wx


# layout 'constants'
print('os.name=%s' % str(os.name))
if os.name == 'nt':
    LeftSpacer = 7            # left border
    RightSpacer = 7           # right border
    TopSpacer = 30            # space at top
    TickSpacer = 30           # space down to ticks
    BotSpacer = 0             # space at the bottom
elif os.name == 'posix':
    LeftSpacer = 3            # left border
    RightSpacer = 3           # right border
    TopSpacer = 3             # space at top
    TickSpacer = 10           # space down to ticks
    BotSpacer = 3             # space at the bottom
else:
    # TODO: Make it work on ???
    raise Exception('Unrecognized platform: %s' % os.name)


################################################################################
# The 'Led16' widget
################################################################################

class Led16(wx.Panel):
    """A custom widget for showing 16 leds."""

    def __init__(self, parent, led_on, led_off, background=None, **kwargs):
        """Initialize an Led16 object.

        parent      owning widget
        led_on      image of led 'on' state
        led_off     image of led 'off' state
        background  widget background colour
        kwargs      extra args for the panel
        """

        print('Led16: background=%s' % str(background))

        wx.Panel.__init__(self, parent, **kwargs)
        if background is not None:
            self.SetBackgroundColour(background)

        self.led_on  = led_on
        self.led_off = led_off
        led_width = led_on.GetWidth()   # assume ON and OFF are same size image
        led_height = led_on.GetHeight()

        x = LeftSpacer
        y = TopSpacer

        mark_count = 2
        self.ticks = [(x-17+led_width, y+led_height/2+5,
                       x-17+led_width, y+led_height/2+10)]
        self.led_posn = []

        # calculate positions of all 16 LEDs and construct ticks draw list
        for i in range(16):
            self.led_posn.append((x-1+i*17, y))
            mark_count += 1
            if mark_count >= 3:
                mark_count = 0
                self.ticks.append((x+i*17 + led_width, y+led_height/2+5,
                                   x+i*17 + led_width, y+led_height/2+10))
        first = self.ticks[0]
        last = self.ticks[-1]
        (fx1, fy1, fx2, fy2) = first
        (lx1, ly1, lx2, ly2) = last
        self.ticks.append((fx1, ly1+5, lx1, ly1+5))

        self.set_value(0)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)

    def OnPaint(self, event):
        # allow transparent colours                                              
        dc = wx.PaintDC(self)
        dc = wx.GCDC(dc)                                                         

        # draw 16 on/off LEDs
        mask = 0x8000
        for i in range(16):
            posn = self.led_posn[i]
            if self.value & mask:
                wx.StaticBitmap(self, -1, self.led_on, pos=posn)
            else:
                wx.StaticBitmap(self, -1, self.led_off, pos=posn)
            mask = mask >> 1

        # draw the tick marks underneath the LEDs
        dc.SetPen(wx.Pen('black', 1))
        dc.DrawLineList(self.ticks)

    def OnSize(self, event):
        self.Refresh()

    def set_value(self, value):
        self.value = value
        self.Refresh()


if __name__ == "__main__":
    import sys

    class MyApp(wx.App):
        def OnInit(self):
            frame = wx.Frame(None, -1, "Test Led16", size=(350, 75))
            vbox = wx.BoxSizer(wx.VERTICAL)

            led_on = wx.Image('images/led_on.png',
                              wx.BITMAP_TYPE_PNG).ConvertToBitmap()

            led_off = wx.Image('images/led_off.png',
                               wx.BITMAP_TYPE_PNG).ConvertToBitmap()

            self.led16 = Led16(frame, led_on, led_off, size=(300,100))
            vbox.Add(self.led16)
            vbox.Fit(frame)
            frame.Show(True)
            self.SetTopWindow(frame)
            self.led16.set_value(012345)
            return True

    app = MyApp(0)

    if len(sys.argv) > 1:
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
