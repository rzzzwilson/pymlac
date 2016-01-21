#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A simulator for an Imlac PDS-1 or PDS-4.

Usage: pymlac [ <option> ]*

That is, the user may specify zero or more options interspersed in any manner
required. The options are:

    -b (ptr | tty | none)         sets the bootstrap ROM code:
                                      ptr   uses the papertape bootstrap ROM
                                      tty   uses the teletype bootstrap ROM
                                      none  uses no bootstrap ROM
    -c                            clears core including bootstrap ROM, if write enabled
    -cf <filename>                sets the name of the core file to read and write
                                  (default file is 'pymlac.core')
    -d <value>                    sets the console data switches to the <value>
    -h                            prints this help
    -ptp <file>                   loads a file on to the papertape punch device
    -ptr <file>                   loads a file on to the papertape reader device
    -r (<address> | pc)           executes from <address> or the current PC contents
    -s <setfile>                  sets memory adress values from <setfile>
    -t (<addr1> [,<addr2>] | off) controls the execution trace:
                                      -t 0100     trace from address 0100 (octal)
                                      -t 0100,200 trace from 0100 octal to 200 decimal
                                      -t off      turns trace off
    -ttyin <file>                 loads a file on to the teletype reader device
    -ttyout <file>                loads a file on to the teletype writer device
    -v <viewfile>                 views contents of memory addresses from file
    -w (on | off)                 controls ROM write property:
                                      -w on     ROM addresses are writable
                                      -w off    ROM addresses are write protected
"""


import sys
import getopt

from Globals import *

import Memory
import MainCPU
import DisplayCPU
import PtrPtp
import TtyIn
import TtyOut
import Trace


class Imlac(object):
    """The Imlac object - contains all devices."""

    def __init__(self):
        self.main_running = False
        self.display_running = False
        self.tracestart = None
        self.traceend = None
        self.DS = 0100000            # dataswitches

        self.memory = Memory.Memory()
        self.ptrptp = PtrPtp.PtrPtp()
        self.cpu = MainCPU.MainCPU(self.memory, None, None,
                                   None, None, None, self.ptrptp)
        self.dcpu = DisplayCPU.DisplayCPU(self.memory)

    def close(corefile=None):
        if corefile:
            self.memory.savecore(corefile)
        sys.exit()

    def set_ROM(type):
        self.memory.set_ROM(type)

    def set_boot(romtype):
        pass

    def __tick_all(cycles):
        self.ptrptp.ptr_tick(cycles)
        self.ptrptp.ptp_tick(cycles)
#        self.ttyin.tick(cycles)
#        self.ttyout.tick(cycles)

    def set_trace(tstart, tend=None):
        """Set trace to required range of values."""

        if tstart:
            self.tracestart = tstart
            self.traceend = tend
            Trace.tracing = True
        else:
            Trace.tracing = False

    def execute_once():
        if self.traceend is None:
            if MainCPU.PC == self.tracestart:
                Trace.settrace(True)
        else:
            Trace.settrace(MainCPU.PC >= self.tracestart
                           and MainCPU.PC <= self.traceend)

        if self.dcpu.ison():
            Trace.trace('%6.6o' % DisplayCPU.DPC)
        Trace.trace('\t')

        instruction_cycles = self.dcpu.execute_one_instruction()

        Trace.trace('%6.6o\t' % MainCPU.PC)

        instruction_cycles += self.cpu.execute_one_instruction()

        Trace.itraceend(DisplayCPU.ison())

        __tick_all(instruction_cycles)

        if not self.dcpu.ison() and not self.cpu.running:
            return 0

        return instruction_cycles

    def run(self):
        """Start the machine and run until it halts."""

        self.cpu.running = True

        while self.execute_once() > 0:
            pass

        self.cpu.running = False

    def set_memory_from_file(self, filename):
        """Set Imlac memory from file."""

        raise Exception('set_memory_from_file: unimplemented')



def str2int(self, s):
    """Convert string to numeric value.

    s  numeric string (decimal or octal)

    Returns the numeric value.
    """

    base = 10
    if s[0] == '0':
        base = 8

    try:
        value = int(s, base=base)
    except:
        return None
    return value


def usage(msg=None):
    if msg:
        print('*'*60)
        print(msg)
        print('*'*60)
    print(__doc__)


def main():
    """Main function of the simulator.  Mostly interpret CLI args.

    Instantiate and run the Imlac object.
    """

    # start wxPython app
    app = wx.App()
    TestFrame().Show()
    app.MainLoop()
    sys.exit(0)

    # create Imlac object with default settings
    imlac = Imlac()

    # read CLI args, left to right and process
    len_sys_argv = len(sys.argv)

    ndx = 1
    while ndx < len_sys_argv:
        opt = sys.argv[ndx]
        ndx += 1
        print('opt=%s' % opt)
        if opt[0] != '-':
            usage("Bad option: '%s'" % str(opt))

        if opt == '-b':
            if ndx >= len_sys_argv:
                usage("'-b' option needs a following device name")
                sys.exit(10)
            dev = sys.argv[ndx].lower()
            ndx += 1
            if dev  == 'ptr':
                imlac.set_ROM('ptr')
            elif dev  == 'tty':
                imlac.set_ROM('tty')
            elif dev  == 'none':
                imlac.set_ROM(None)
            else:
                usage("-b option must be followed by 'ptr', 'tty' or 'none'")
                sys.exit(10)
        elif opt == '-c':
            imlac.memory.clear_core()
        elif opt == '-cf':
            if ndx >= len_sys_argv:
                usage("'-cf' option needs a following filename")
                sys.exit(10)
            filename = sys.argv[ndx]
            ndx += 1
            imlac.memory.set_corefile(filename)
        elif opt == '-d':
            if ndx >= len_sys_argv:
                usage("'-d' option needs a following data switch value")
                sys.exit(10)
            value = str2int(sys.argv[ndx])
            ndx += 1
            if value is None:
                usage("The '-d' option must be followed by a decimal or octal value")
                sys.exit(10)
            imlac.cpu.set_dataswitches(value)
        elif opt == '-h':
            usage()
            sys.exit(0)
        elif opt == '-ptp':
            if ndx >= len_sys_argv:
                usage("'-ptp' option needs a following PTP filename")
                sys.exit(10)
            filename = sys.argv[ndx]
            ndx += 1
            imlac.ptrptp.ptp_mount(filename)
        elif opt == '-ptr':
            if ndx >= len_sys_argv:
                usage("'-ptr' option needs a following PTR filename")
                sys.exit(10)
            filename = sys.argv[ndx]
            ndx += 1
            imlac.ptrptp.ptr_mount(filename)
        elif opt == '-r':
            if ndx >= len_sys_argv:
                usage("'-r' option needs a following address or 'pc'")
                sys.exit(10)
            address = sys.argv[ndx].lower()
            ndx += 1
            if address != 'pc':
                addr_value = str2int(address)
                if addr_value is None:
                    usage("'-r' option needs a following address or 'pc'")
                    sys.exit(10)
                self.cpu.PC = addr_value
            imlac.run()
        elif opt == '-s':
            if ndx >= len_sys_argv:
                usage("'-s' option needs a following data filename")
                sys.exit(10)
            filename = sys.argv[ndx]
            ndx += 1
            imlac.set_memory_from_file(filename)
        elif opt == '-t':
            if ndx >= len_sys_argv:
                usage("'-t' option needs a following address range or 'off'")
                sys.exit(10)
            r = sys.argv[ndx]
            ndx += 1
            if r == 'off':
                set_trace_off()
            else:
                if ',' in r:
                    rr = r.split(',')
                    if len(rr) != 2:
                        usage("'-r' option may be followed by only two addresses")
                        sys.exit(10)
                    (start, stop) = rr
                    start_addr = str2int(start)
                    stop_addr = str2int(stop)
                else:
                    start_addr = str2int(r)
                    stop_addr = None
                imlac.set_trace(star_addr, stop_addr)
        elif opt == '-ttyin':
            raise Exception('-ttyin: Unimplemented')
#            if ndx >= len_sys_argv:
#                usage("'-ttyin' option needs a following data filename")
#                sys.exit(10)
#            filename = sys.argv[ndx]
#            ndx += 1
#            set_tty_in(filename)
        elif opt == '-ttyout':
            raise Exception('-ttyout: Unimplemented')
#            if ndx >= len_sys_argv:
#                usage("'-ttyout' option needs a following data filename")
#                sys.exit(10)
#            filename = sys.argv[ndx]
#            ndx += 1
#            set_tty_out(filename)
        elif opt == '-v':
            raise Exception('-ttyout: Unimplemented')
#            if ndx >= len_sys_argv:
#                usage("'-v' option needs a following address filename")
#                sys.exit(10)
#            filename = sys.argv[ndx]
#            ndx += 1
#            view_mem(filename)
        elif opt == '-w':
            if ndx >= len_sys_argv:
                usage("'-v' option needs a following 'on' or 'off'")
                sys.exit(10)
            state = sys.argv[ndx]
            ndx += 1
            if state == 'on':
                state = False
            elif state == 'off':
                state = True
            else:
                usage("'-v' option needs a following 'on' or 'off'")
                sys.exit(10)
            self.memory.set_ROM_writable(state)


if __name__ == '__main__':
    main()
