#!/usr/bin/python

"""
The Imlac trace stuff.

Simple usage:
    import Trace
    trace = Trace.Trace('my_log.log', maincpu, dispcpu)
    trace.itrace(msg)

Based on the 'borg' recipe from [http://code.activestate.com/recipes/66531/].
"""

import os

from Globals import *


class Trace(object):

    __shared_state = {}                # this __dict__ shared by ALL instances

    def __init__(self, filename, maincpu=None, displaycpu=None):
        """Initialize the trace:

        filename   name of the trace file
        maincpu    the main CPU object (may be added later)
        displaycpu  the display CPU object (may be added later)
        """

        # ensure same state as all other instances
        self.__dict__ = Trace.__shared_state

        # set internal state
        self.tracing = True
        self.tracefile = filename
        try:
            os.remove(filename)
        except:
            pass
        self.tracefile = open(filename, 'wb')
        self.tracefile.write('%s trace\n%s\n' % (PYMLAC_VERSION, '-'*60))

        self.cpu = maincpu
        self.dcpu = displaycpu

    def add_maincpu(self, maincpu):
        """Add the main CPU object."""

        self.cpu = maincpu

    def add_dispcpu(self, dispcpu):
        """Add the display CPU object."""

        self.dcpu = dispcpu

    def close(self):
        """Close trace."""

        self.tracefile.close()
        self.tracing = False
        self.tracefile = None

    def deimtrace(self, opcode, code):
        """Trace the DEIM instruction.

        opcode  DEIM opcode
        code    the operation
        """

        if self.tracing:
            self.tracefile.write('%s\t%s\t' % (opcode, code))
            self.tracefile.flush()

    def dtrace(self, opcode, address=None):
        """Trace the display CPU.

        opcode   display opcode
        address  address for the opcode
        """

        if self.tracing:
            if address is None:
                self.tracefile.write('%s\t\t' % opcode)
            else:
                self.tracefile.write('%s\t%5.5o\t' % (opcode, address))
            self.tracefile.flush()

    def itrace(self, opcode, indirect=False, address=None):
        """Main CPU trace.

        opcode   the main CPU opcode
        indirect  True if instruction was indirect
        adress    address for the instruction (if any)
        """

        if self.tracing:
            char = '*' if indirect else ''
            if address is None:
                self.tracefile.write('%s\t%s\t' % (opcode, char))
            else:
                self.tracefile.write('%s\t%s%5.5o\t' % (opcode, char, address))
            self.tracefile.flush()

    def itraceend(self, dispon):
        """Trace at the end of one execution cycle.

        dispon  True if the display was on
        """

        self.tracefile.write('L=%1.1o AC=%6.6o PC=%6.6o'
                             % (self.cpu.L, self.cpu.AC, self.cpu.PC))

        if dispon:
            self.tracefile.write(' DX=%5.5o DY=%6.6o'
                                 % (self.dcpu.DX, self.dcpu.DY))
        self.tracefile.write('\n')

        self.tracefile.flush()

    def comment(self, msg):
        """Add a comment to the trace."""

        self.tracefile.write(msg+'\n')
        self.tracefile.flush()

    def settrace(self, new_tracing):
        """Set the trace ON or OFF."""

        self.tracing = new_tracing
