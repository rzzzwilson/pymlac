#!/usr/bin/env python

import time
import collections
import threading

import wx 

WIDTH_SCREEN = 1024
HEIGHT_SCREEN = 1024
WIDTH_CONSOLE = 400 # 256
HEIGHT_CONSOLE = HEIGHT_SCREEN

SCREEN_COLOUR = (0, 0, 0)
CONSOLE_COLOUR = (223, 223, 169)
#PHOSPHOR_COLOUR = '#F0F000'	# yellow
PHOSPHOR_COLOUR = '#40FF40'	# green

L_AC_MARGIN = 30
CTL_MARGIN = 10 # 38 # 15
LED_MARGIN = 5

IMAGE_LED_OFF = 'images/led_off.png'
IMAGE_LED_ON = 'images/led_on.png'

count = 1

HALF_SCREEN = HEIGHT_SCREEN/2


class ImlacCpuThread(threading.Thread):

    def __init__(self, report_win, queue):

        threading.Thread.__init__(self)
        self.report_win = report_win
        self.queue = queue
        self.running = True
        self.start()

    def run(self):
        # This is the code executing in the new thread. Simulation of
        # a long process (well, 10s here) as a simple loop - you will
        # need to structure your processing so that you periodically
        # peek at the abort variable
        left_offset = 0
        right_offset = HEIGHT_SCREEN - 1
        top_offset = 0
        bottom_offset = HEIGHT_SCREEN - 1
        shrink = True

        while self.running:
            time.sleep(0.005)
            if shrink:
                left_offset += 1
                right_offset -= 1
                top_offset += 1
                bottom_offset -= 1
                if left_offset >= HALF_SCREEN:
                    shrink = False
            else:
                left_offset -= 1
                right_offset += 1
                top_offset -= 1
                bottom_offset += 1
                if left_offset < 0:
                    shrink = True
            draw_list = ((left_offset, top_offset, right_offset, top_offset),
                         (right_offset, top_offset, right_offset, bottom_offset),
                         (left_offset, bottom_offset, right_offset, bottom_offset),
                         (left_offset, top_offset, left_offset, bottom_offset),
                         (left_offset, 511, 511, top_offset),
                         (511, top_offset, right_offset, 511),
                         (right_offset, 511, 511, bottom_offset),
                         (511, bottom_offset, left_offset, 511))
            self.queue.append(draw_list)

    def abort(self):
        """abort CPU thread."""

        # Method for use by main thread to signal an abort
        self.running = False
        self.join()


class Led_1(object):
    def __init__(self, parent, label, x, y, off, on):
        wx.StaticText(parent, -1, label, pos=(x, y))
        y += 15
        wx.StaticBitmap(parent, -1, off, pos=(x-1, y))
        self.led = wx.StaticBitmap(parent, -1, on, pos=(x-1, y))
        self.set_value(0)

    def set_value(self, value):
        if value:
            self.led.Enable()
        else:
            self.led.Disable()
        

class Led_16(object):
    def __init__(self, parent, label, x, y, off, on):
        led_width = off.GetWidth()
        led_height = off.GetHeight()
        wx.StaticText(parent, -1, label, pos=(x, y))
        y += 15
        self.leds = []
        mark_count = 2
        self.ticks = [(x-17+led_width, y+led_height/2+5,
                       x-17+led_width, y+led_height/2+10)]
        for i in range(16):
            #wx.StaticBitmap(parent, -1, off, pos=(x-1+i*17, y))
            led = wx.StaticBitmap(parent, -1, on, pos=(x-1+i*17, y))
            self.leds.append(led)
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

    def paint(self, dc):
        dc.SetPen(wx.Pen('black', 1))
        dc.DrawLineList(self.ticks)

    def set_value(self, value):
        mask = 0x8000
        for l in self.leds:
            if value & mask:
                l.Enable()
            else:
                l.Disable()
            mask = mask >> 1
        

class MyFrame(wx.Frame): 
    """a frame with two panels"""
    def __init__(self, parent=None, id=-1, title=None): 
        wx.Frame.__init__(self, parent, id, title) 
        self.panel_Screen = wx.Panel(self,
                                     size=(WIDTH_SCREEN, HEIGHT_SCREEN),
                                     pos=(0,0)) 
        self.panel_Screen.SetBackgroundColour(SCREEN_COLOUR)
        self.panel_Console = wx.Panel(self, style=wx.SIMPLE_BORDER,
                                      size=(WIDTH_CONSOLE, HEIGHT_SCREEN),
                                      pos=(WIDTH_SCREEN,0)) 
        self.panel_Console.SetBackgroundColour(CONSOLE_COLOUR)

        led_off = wx.Image('images/led_off.png',
                           wx.BITMAP_TYPE_PNG).ConvertToBitmap()
        led_on = wx.Image('images/led_on.png',
                          wx.BITMAP_TYPE_PNG).ConvertToBitmap()

        y_pos = 8
        self.led_l = Led_1(self.panel_Console, 'l', CTL_MARGIN, y_pos,
                           led_off, led_on)
        self.led_ac = Led_16(self.panel_Console, 'ac', 3*CTL_MARGIN, y_pos,
                             led_off, led_on)
        y_pos += 35
        self.led_pc = Led_16(self.panel_Console, 'pc', 3*CTL_MARGIN, y_pos,
                             led_off, led_on)


        y_pos = 305
        wx.StaticText(self.panel_Console, -1, 'ptr', pos=(CTL_MARGIN, y_pos))
        y_pos += 15
        self.txt_ptrFile = wx.TextCtrl(self.panel_Console, -1,
                                       pos=(CTL_MARGIN, y_pos),
                                       size=(WIDTH_CONSOLE-2*CTL_MARGIN, 25))
        y_pos += 30

        wx.StaticText(self.panel_Console, -1, 'ptp', pos=(CTL_MARGIN, y_pos))
        y_pos += 15
        self.txt_ptpFile = wx.TextCtrl(self.panel_Console, -1,
                                       pos=(CTL_MARGIN, y_pos),
                                       size=(WIDTH_CONSOLE-2*CTL_MARGIN, 25))
        y_pos += 15

        self.y_offset = 0
        self.y_sign = +1

        #self.panel_Screen.Bind(wx.EVT_PAINT, self.on_paint) 
        #self.panel_Console.Bind(wx.EVT_PAINT, self.on_paint) 
        self.Bind(wx.EVT_PAINT, self.on_paint) 
        self.Bind(wx.EVT_CLOSE, self.onClose)

        self.Fit() 

        self.queue = collections.deque()
        self.draw_list = []
        self.worker = ImlacCpuThread(self, self.queue)


    def on_paint(self, event=None):
        global count

        # draw the LED ticks
        dc = wx.PaintDC(self.panel_Console)
        self.led_ac.paint(dc)
        self.led_pc.paint(dc)

        # establish the painting surface
        dc = wx.PaintDC(self.panel_Screen)
        dc.SetBackground(wx.Brush(SCREEN_COLOUR, 1))
        dc.SetPen(wx.Pen(PHOSPHOR_COLOUR, 1))
        dc.Clear()

        if len(self.queue):
            self.draw_list = self.queue.pop()
            self.queue.clear()
        
        for args in self.draw_list:
            dc.DrawLine(*args)

        count += 1
        self.led_ac.set_value(count)
        print('count=%d' % count)

    def onClose(self, event):
        self.worker.abort()
        print('after abort()')
        self.Destroy()
        print('after Destroy()')


# test it ...
app = wx.PySimpleApp() 
frame1 = MyFrame(title='pymlac 0.1') 
frame1.Center() 
frame1.Show() 
app.MainLoop()
