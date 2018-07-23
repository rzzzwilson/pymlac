"""
The Imlac display.

A temporary version that outputs a PPM graphics image.

The Imlac dislay X and Y registers are of size 11 bits.  The most significant
6 bits are the MSB and the least significant 5 bits are the LSB.  A DLXA (or
DLYA) loads the display X (or Y) register from the 10 bits of valu, with bit
10 of the X/Y register being set to 0.

The virtual display is 2048x2048 pixels, but the physical display is
1024x1024 pixels.
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

#    BackgroundColour = 'black'
#    DrawColour = '#ffff88'

    SYNC_HZ = 40
    SYNC_40HZ_CYCLE_COUNT = int(CYCLES_PER_SECOND / SYNC_HZ)

    BackgroundColour = 1
    DrawColour = 0

    # max coordinates of pymlac physical display
    ScaleMaxX = 1024
    ScaleMaxY = 1024


    def __init__(self):
        # create and initialise the image array
        # reference .array[y*ScaleMaxX + x]
        self.array = [self.BackgroundColour] * self.ScaleMaxY * self.ScaleMaxX

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
        filename = 'pymlac_%06d.pbm' % self.next_file_num
        with open(filename, 'wb') as handle:
            # output header data
            handle.write(bytes('P1\n', 'utf-8'))
            handle.write(bytes('# created by pymlac %s\n' % __version__, 'utf-8'))
            handle.write(bytes('%d %d\n' % (self.ScaleMaxX, self.ScaleMaxY), 'utf-8'))

            # output graphics data
            for v in self.array:
                handle.write(bytes('%d\n' % v, 'utf-8'))

        self.dirty = False

        log('Display: array written to file %s' % filename)

    def draw(self, x1, y1, x2, y2, dotted=False):
        """Draw a line on the screen.

        x1, y1  start coordinates
        x2, y2  end coordinates
        dotted  True if dotted line, else False (IGNORED)

        Algorithm from:
            http://csourcecodes.blogspot.com/2016/06/bresenhams-line-drawing-algorithm-generalized-c-program.html
        """

        # convert virtual coords to physical
        x1 = x1 // 2
        y1 = y1 // 2
        x2 = x2 // 2
        y2 = y2 // 2

        # invert the Y axis
        y1 = self.ScaleMaxY - y1
        y2 = self.ScaleMaxY - y2

        # draw the line (Bresenham algorithm)
        x = x1
        y = y1
        dx = abs(x2 - x1)
        dy = abs(y2 - y1)
        s1 = 1 if x2 > x1 else -1       # sign(x2 - x1)
        s2 = 1 if y2 > y1 else -1       # sign(y2 - y1)
        swap = False
        self.array[(y-1)*self.ScaleMaxX + x - 1] = self.DrawColour
        if dy > dx:
            (dx, dy) = (dy, dx)
            swap = True
        p = 2*dy - dx
        for i in range(0, dx):
            self.array[(y-1)*self.ScaleMaxX + x - 1] = self.DrawColour
            while p >= 0:
                p = p - 2*dx
                if swap:
                    x += s1
                else:
                    y += s2
            p = p + 2*dy
            if swap:
                y += s2
            else:
                x += s1
            i += 1

        # set display flag to "changed"
        self.dirty = True

    def clear(self):
        """Clear the display."""

        log('Display: clearing the display')

        # write display to next PPM file first
        if self.dirty:
            self.write()
            self.array = [self.BackgroundColour] * self.ScaleMaxY * self.ScaleMaxX
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


if __name__ == '__main__':
    """Test case - draw radial lines."""

    d = Display()
    granularity = 32
    for x in range(0, 2048, granularity):
        d.draw(x, 0, 1023, 1023)
    for y in range(0, 2048, granularity):
        d.draw(2048, y, 1023, 1023)
    for x in range(2048, 0, -granularity):
        d.draw(x, 2048, 1023, 1023)
    for y in range(2048, 0, -granularity):
        d.draw(0, y, 1023, 1023)
    d.clear()
    d.close()
