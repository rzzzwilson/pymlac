#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
The Imlac display.

A temporary version that outputs a PPM graphics image.
"""


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


################################################################################
# The actual pymlc display widget.
################################################################################

class Display(object):

    BackgroundColour = 'black'
    DrawColour = '#ffff88'

    SYNC_HZ = 40
    SYNC_40HZ_CYCLE_COUNT = int(CYCLES_PER_SECOND / SYNC_HZ)

    # max coordinates of pymlac display
#    ScaleMaxX = 2048
#    ScaleMaxY = 2048
    ScaleMaxX = 1024
    ScaleMaxY = 1024


    def __init__(self, parent, **kwargs):
        # create and initialise the image array
        # reference .array[y*ScaleMaxX + x]
        self.array = [0] * self.ScaleMaxY * self.ScaleMaxX

        # set internal state
        self.running = 0
        self.cycle_count = 0
        self.Sync40hz = 1
        self.next_file_num = 0

        # 'dirty' flag set after writing
        self.dirty = False 

    def write(self):
        """Write display array to PPM file."""

        self.next_file_num += 1
        filename = 'pymlac_%06d.ppm' % self.next_file_num
        with open(filename, 'wb') as handle:
            # output header data
            handle.write('P1\n')
            handle.write('# created by pymlac %s\n' % __version__)
            handle.write('%d %d\n' % (self.ScaleMaxX, self.ScaleMaxY))
            handle.write('1\n')

            # output graphics data
            for v in self.array:
                handle.write('%d\n' % v)
        self.dirty = False

    def draw(self, x1, y1, x2, y2, dotted=False):
        """Draw a line on the screen.

        x1, y1  start coordinates
        x2, y2  end coordinates
        dotted  True if dotted line, else False (IGNORED)
        """

        self.dirty = True

        # draw a straight line using Breshenam
        self.bresenham(x1, y1, x2, y2)

    def clear(self):
        """Clear the display."""

        # write display to next PPM file first
        if self.dirty:
            self.write()
            self.array = [0] * self.ScaleMaxY * self.ScaleMaxX
            self.dirty = False

    def syncclear(self):
        self.Sync40hz = 0
        self.cycle_count = self.SYNC_40HZ_CYCLE_COUNT

    def ready(self):
        return self.Sync40hz

    def tick(self, cycles):
        """Advance the internal state by given cycles."""

        self.cycle_count -= cycles
        if self.cycle_count <= 0:
            self.Sync40hz = 1
            self.cycle_count = 0

    def close(self):
        """Close display, writing data if 'dirty'."""

        if self.dirty:
            self.write()

    def bresenham(self, x1, y1, x2, y2):
        """Draw a straight line on the graphics array."""

# algorithm from:
# http://www.idav.ucdavis.edu/education/GraphicsNotes/Bresenhams-Algorithm.pdf
#       Let ∆x = x2 − x1
#       Let ∆y = y2 − y1
#       Let j = y1
#       Let ε = ∆y − ∆x
#
#       for i = x1 to x2−1
#           illuminate (i, j)
#           if (ε ≥ 0)
#               j += 1
#               ε −= ∆x
#           end if
#           i += 1
#           ε += ∆y
#       next i
#
#       finish

        dx = x2 - x1
        dy = y2 - y1
        j = y1
        sigma = dy = dx

        for i in range(x1, x2):
            #illuminate(i, j)
            self.array[j*self.ScaleMaxX + i]
            if sigma >= 0:
                j += 1
                sigma -= dx
            i += 1
            sigma += dy
