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
# The actual pymlac display widget.
# This version is just a debug version that creates PPM files.
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


    def __init__(self):
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

        log('Display: instance created')

    def write(self):
        """Write display array to PPM file."""

        self.next_file_num += 1
        filename = 'pymlac_%06d.ppm' % self.next_file_num
        with open(filename, 'wb') as handle:
            # output header data
            handle.write('P1\n')
            handle.write('# created by pymlac %s\n' % __version__)
            handle.write('%d %d\n' % (self.ScaleMaxX, self.ScaleMaxY))

            # output graphics data
            for v in self.array:
                handle.write('%d\n' % v)

        self.dirty = False

        log('Display: array written to file %s' % filename)

    def draw(self, x1, y1, x2, y2, dotted=False):
        """Draw a line on the screen.

        x1, y1  start coordinates
        x2, y2  end coordinates
        dotted  True if dotted line, else False (IGNORED)
        """

#        log('Display: drawing (%d,%d) to (%d,%d)' % (x1, y1, x2, y2))

        self.dirty = True

        # draw a straight line using Bresenam
        self.bresenham(x1, y1, x2, y2)

    def clear(self):
        """Clear the display."""

        log('Display: clearing the display')

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

# original algorithm from:
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

    def bresenham(self, x1, y1, x2, y2):
        """Bresenham algorithm to draw from (x1,y1) to (x2,y2)."""

        dx = x2 - x1
        dy = y2 - y1

        # Determine how steep the line is
        is_steep = abs(dy) > abs(dx)

        # Rotate line
        if is_steep:
            x1, y1 = y1, x1
            x2, y2 = y2, x2

        # Swap start and end points if necessary and store swap state
        swapped = False
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
            swapped = True

        # Recalculate differentials
        dx = x2 - x1
        dy = y2 - y1

        # Calculate error
        error = int(dx / 2.0)
        ystep = 1 if y1 < y2 else -1

        # Iterate over bounding box generating points between start and end
        y = y1
        for x in range(x1, x2 + 1):
            (xx, yy) = (y, x) if is_steep else (x, y)
            self.array[yy*self.ScaleMaxX + xx] = 1
            error -= abs(dy)
            if error < 0:
                y += ystep
                error += dx


if __name__ == '__main__':
    """Test case - draw radial lines."""

    d = Display()
    d.draw(0, 0, 1023, 1023)
    d.draw(255, 0, 1023-255, 1023)
    d.draw(511, 0, 1023-511, 1023)
    d.draw(767, 0, 1023-767, 1023)
    d.draw(1023, 0, 0, 1023)
    d.draw(0, 255, 1023, 1023-255)
    d.draw(0, 511, 1023, 1023-511)
    d.draw(0, 767, 1023, 1023-767)
    d.close()
