"""
The Imlac trace stuff.

Simple usage:
    import Trace
    Trace.init('my_log.log', maincpu, dispcpu)
    Trace.set_trace_map(map)
    while running:
        Trace.start()
        Trace.itrace(inst_str)
        Trace.dtrace(inst_str)
        Trace.end()

The idea is that trace system will handle formatting and writing trace data to
the trace file and the "main" code will perform the above steps.  The
.endtrace() method will grab the register values after the instructions and
format the trace data and write it to the file.
"""

import os
import collections

from Globals import *

import log
log = log.Log('test.log', log.Log.DEBUG)


Tracing = False
TrafeFilename = None
TraceFile = None
CPU = None
DCPU = None
TraceMap = collections.defaultdict(bool)
CPUInst = ''
DCPUInst = ''
CPU_PC = None
DCPU_PC = None


def init(filename, maincpu=None, displaycpu=None):
    """Initialize the trace:

    filename    name of the trace file
    maincpu     the main CPU object (may be added later)
    displaycpu  the display CPU object (may be added later)
    """

    global Tracing, TraceFile, TraceFilename, TraceMap
    global CPU, DCPU, CPUInst, DCPUInst

    # set internal state
    Tracing = True
    TraceFilename = filename
    try:
        os.remove(filename)
    except:
        pass
    TraceFile = open(filename, 'w')
    TraceFile.write(f"{PYMLAC_VERSION} trace\n{'-'*97}\n")

    CPU = maincpu
    DCPU = displaycpu

def start():
    """Prepare trace system for new execution."""

    global CPU_PC, DCPU_PC, CPUInst, DCPUInst

    CPUInst = ''
    DCPUInst = ''
    CPU_PC = CPU.PC
    DCPU_PC = DCPU.DPC

def set_TraceMap(trace_map):
    """Set the trace address dict mapping."""

    global TraceMap

    TraceMap = trace_map
    log(f'Trace.set_TraceMap: TraceMap={TraceMap}')

def add_CPU(maincpu):
    """Add the main CPU object."""

    global CPU

    CPU = maincpu

def add_DCPU(dispcpu):
    """Add the display CPU object."""

    global DCPU
    DCPU = dispcpu

def close():
    """Close trace."""

    global TraceFile, Tracing

#    TraceFile.close()
    TraceFile = None
    Tracing = False

#def deimtrace(opcode, code):
#    """Trace the DEIM instruction.
#
#    opcode  DEIM opcode
#    code    the operation
#    """
#
#    log(f"deimtrace: Tracing={Tracing}, writing '{opcode} {code}'")
#    if Tracing:
#        TraceFile.write('%s %s\t' % (opcode, code))
#        TraceFile.flush()

def dtrace(ddot, opcode, address=None):
    """Trace the display CPU.

    ddot     address of instruction being traced
    opcode   display opcode
    address  address for the opcode

    Places the final trace string into DCPUInst.
    """

    global DCPUInst

    log(f'Trace.dtrace: ddot={ddot}, opcode={opcode}, address={address}')

    # convert an int address to a string
    if isinstance(address, int):
        address = f'{address:05o}'

    if Tracing:
        if address is None:
            DCPUInst = '%04o    %s' % (ddot, opcode)
        else:
            DCPUInst = '%04o    %s %s' % (ddot, opcode, address)

    log(f"dtrace: DCPUInst='{DCPUInst}'")

def itrace(dot, opcode, indirect=False, address=None):
    """Main CPU trace.

    dot       address of instruction being traced
    opcode    the main CPU opcode
    indirect  True if instruction was indirect
    address   address for the instruction (if any)

    Places the final trace string in CPUInst.
    """

    global CPUInst

    log(f'itrace: dot={dot}, opcode={opcode}, indirect={indirect}, address={address}')
    log(f'itrace: Tracing={Tracing}, TraceMap[dot]={TraceMap[dot]}')

    if Tracing and TraceMap[dot]:
        char = '*' if indirect else ''
        if address is None:
            CPUInst = '%04o     %s %s' % (dot, opcode, char)
        else:
            CPUInst = '%04o     %s %s%5.5o' % (dot, opcode, char, address)

    log(f"itrace: CPUInst='{CPUInst}'")

#def itraceend(dispon):
#    """Trace at the end of one execution cycle.
#
#    dispon  True if the display was on
#
#    Places the final trace string in DCPUInst.
#    """
#
#    global DCPUInst
#
#    DCPUInst = f'L={CPU.L:1.1o} AC={CPU.AC:6.6oi} PC={CPU.PC:6.6o}'
#
#    if dispon:
#        DCPUInst += ' DX=%5.5o DY=%5.5o' % (DCPU.DX, DCPU.DY)

def end_line():
    """Write the line for this set of I/D instructions."""

    registers = f'L={CPU.L:1o} AC={CPU.AC:6o} PC={CPU.PC:6o}'

    if DCPU.Running:
        registers += f' DX={DCPU.DX:5o} DY={DCPU.DY:5o}'

    TraceFile.write('%-25s %-30s%s\n' % (CPUInst, DCPUInst, registers))

def flush():
    TraceFile.flush()

def comment(msg):
    """Write a line to the trace file."""

    TraceFile.write(msg + '\n')
    TraceFile.flush()

def settrace(new_tracing):
    """Set the trace ON or OFF."""

    global Tracing

    Tracing = new_tracing
    log(f'Trace.settrace: Tracing={Tracing}')
