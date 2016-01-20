#!/usr/bin/python

"""
The Imlac emulation object.
"""


import sys

from Globals import *

import PtrPtp
import TtyIn
import TtyOut
import Memory
import MainCPU
import DisplayCPU
import Trace



class Imlac(object):
    """The Imlac object - contains all devices."""

    def __init__(self):
        self.main_running = False
        self.display_running = False
        self.tracestart = None
        self.traceend = None
        self.DS = 0100000            # dataswitches

    def init(self, run_address, tracefile, tstart, tend,
             boot_rom=None, corefile=None):

        Memory.init(boot_rom, corefile)
        Trace.init(tracefile)
        self.tracestart = tstart
        self.traceend = tend

    def close(corefile=None):
        if corefile:
            Memory.savecore(corefile)
        sys.exit()

    def set_ROM(type):
        Memory.set_ROM(type)

    def set_boot(romtype):
        pass

    def __tick_all(cycles):
        PtrPtp.ptr_tick(cycles)
        PtrPtp.ptp_tick(cycles)
        TtyIn.tick(cycles)
        TtyOut.tick(cycles)

    def set_trace(tstart, tend=None):
        """Set trace to required range of values."""

        global tracestart, traceend

        if tstart:
            tracestart = tstart
            traceend = tend
            Trace.tracing = True
        else:
            Trace.tracing = False

    def execute_once():
        if traceend is None:
            if MainCPU.PC == tracestart:
                Trace.settrace(True)
        else:
            Trace.settrace(MainCPU.PC >= tracestart and MainCPU.PC <= traceend)

        if DisplayCPU.ison():
            Trace.trace('%6.6o' % DisplayCPU.DPC)
        Trace.trace('\t')

        instruction_cycles = DisplayCPU.execute_one_instruction()

        Trace.trace('%6.6o\t' % MainCPU.PC)

        instruction_cycles += MainCPU.execute_one_instruction()

        Trace.itraceend(DisplayCPU.ison())

        __tick_all(instruction_cycles)

        if not DisplayCPU.ison() and not MainCPU.running:
            return 0

        return instruction_cycles

    def run():
        """Start the machine and run until it halts."""

        MainCPU.running = True

        while execute_once() > 0:
            pass

        MainCPU.running = False

