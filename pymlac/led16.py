#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The 'led16' widget.

Event attributes:
    'state' - the current displayed value (int)

Instance methods:
    Led16(parent, label, pos, led, *args, **kwargs)
        parent      owning widget
        label       label above leftmost led
        pos         position (x, y)
        led         image of led 'on' state
        args        ?
        kwargs      ?
    SetState(state)
        sets widget state, 'state' is as in constructor.

The widget will look like:

             +-<title>----------------------------+
             |                 <TopSpacer>        |
 LeftSpacer--+-> O O O O O O O O O O O O O O O O  |\TickSpacer
             |  +-+-----+-----+-----+-----+-----+ |/
             |                 <BotSpacer>        |
             +------------------------------------+


-
|top spacer
-
|-------------|<label>  --label spacer
left spacer             /
               O O O O O O O O O O O O O O O O  --tick spacer
              +-+-----+-----+-----+-----+-----+ /
-                            ^
|bot spacer                  |
-                         octal ticks
"""

import os
import wx


# layout 'constants'
if os.name == 'nt':
    LeftSpacer = 7            # left border
    TopSpacer = 30
    TickSpacer = 30
    BotSpacer = 0             # space between ticks and box
elif os.name == 'posix':
    LeftSpacer = 3            # left border
    TopSpacer = 10            # space between top box and label
    LabelSpacer = 10
    TickSpacer = 30
    BotSpacer = 10            # space between ticks and box
else:
    # TODO: Make it work on Mac
    raise Exception('Unrecognized platform: %s' % os.name)


################################################################################
# The 'Led16' widget
################################################################################

class Led16(wx.Panel):
    """A custom widget for showing 16 leds."""

    def __init__(self, parent, label, led_img, background=None, *args, **kwargs):
        """Initialize an Led16 object.

        parent      owning widget
        label       label above leftmost led
        led_img     image of led 'on' state
        background  widget background colour
        args        ?
        kwargs      ?
        """

        wx.Panel.__init__(self, parent, *args, **kwargs)
        self.SetBackgroundColour(background)

        x = LeftSpacer
        y = TopSpacer
        led_width = led_img.GetWidth()
        led_height = led_img.GetHeight()

        label = ' ' + label.strip() + ' '
        sbox = wx.StaticBox(self, label=label)
        vbox = wx.StaticBoxSizer(sbox, wx.VERTICAL)

        vbox.AddSpacer(BotSpacer)
        y += LabelSpacer

        #hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.leds = []
        mark_count = 2
        self.ticks = [(x-17+led_width, y+led_height/2+5,
                       x-17+led_width, y+led_height/2+10)]
        for i in range(16):
            led = wx.StaticBitmap(self, -1, led_img, pos=(x-1+i*17, y))
            #hbox.Add(led)
            self.leds.append(led)
            mark_count += 1
            if mark_count >= 3:
                mark_count = 0
                self.ticks.append((x+i*17 + led_width, y+led_height/2+5,
                                   x+i*17 + led_width, y+led_height/2+10))
        vbox.Add(hbox)

        first = self.ticks[0]
        last = self.ticks[-1]
        (fx1, fy1, fx2, fy2) = first
        (lx1, ly1, lx2, ly2) = last
        self.ticks.append((fx1, ly1+5, lx1, ly1+5))

        vbox.AddSpacer(BotSpacer)

        self.set_value(0)

        self.SetSizer(vbox)

        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.Bind(wx.EVT_SIZE, self.OnSize)


    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.SetPen(wx.Pen('black', 1))
        dc.DrawLineList(self.ticks)


    def OnSize(self, event):
        self.Refresh()


    def set_value(self, value):
        mask = 0x8000
        for l in self.leds:
            if value & mask:
                l.Enable()
            else:
                l.Disable()
            mask = mask >> 1


if __name__ == "__main__":
    import sys

    class MyApp(wx.App):
        def OnInit(self):
            frame = wx.Frame(None, -1, "Test Led16", size=(350, 75))
            vbox = wx.BoxSizer(wx.VERTICAL)

            led = wx.Image('images/led_on.png', wx.BITMAP_TYPE_PNG).ConvertToBitmap()

            self.led16 = Led16(frame, 'Led16', led, size=(300,100))
            vbox.Add(self.led16)
            vbox.Fit(frame)
            frame.Show(True)
            self.SetTopWindow(frame)
            self.led16.set_value(0xfffe)
            return True

    app = MyApp(0)

    if len(sys.argv) > 1:
        import wx.lib.inspection
        wx.lib.inspection.InspectionTool().Show()

    app.MainLoop()
