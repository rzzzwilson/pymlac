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
import collections

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

        self.trace_map = collections.defaultdict(bool)

    def set_trace_map(self, trace_map):
        """Set the trace address dict mapping."""

        self.trace_map = trace_map

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

    def dtrace(self, ddot, opcode, address=None):
        """Trace the display CPU.

        ddot     address of instruction being traced
        opcode   display opcode
        address  address for the opcode

        Returns the trace string or None if not tracing.
        """

        result = None

        if self.tracing:
            if address is None:
                result = '%04o: %s\t' % (ddot, opcode)
            else:
                result = '%04o: %s\t%5.5o' % (ddot, opcode, address)

        return result

    def itrace(self, dot, opcode, indirect=False, address=None):
        """Main CPU trace.

        dot       address of instruction being traced
        opcode    the main CPU opcode
        indirect  True if instruction was indirect
        address   address for the instruction (if any)

        Returns the trace string or None if not tracing.
        """

        result = None
        if self.tracing and self.trace_map[dot]:
            char = '*' if indirect else ''
            if address is None:
                result = '%04o\t%s\t%s' % (dot, opcode, char)
            else:
                result = '%04o\t%s\t%s%5.5o' % (dot, opcode, char, address)

        return result

    def itraceend(self, dispon):
        """Trace at the end of one execution cycle.

        dispon  True if the display was on

        Returns the trace string.
        """

        result = ('L=%1.1o AC=%6.6o PC=%6.6o'
                  % (self.cpu.L, self.cpu.AC, self.cpu.PC))

        if dispon:
            result += ' DX=%5.5o DY=%5.5o' % (self.dcpu.DX, self.dcpu.DY)

        return result

    def flush(self):
        self.tracefile.flush()

    def comment(self, msg):
        """Write a line to the trace file."""

        self.tracefile.write(msg+'\n')
        self.tracefile.flush()

    def settrace(self, new_tracing):
        """Set the trace ON or OFF."""

        self.tracing = new_tracing
