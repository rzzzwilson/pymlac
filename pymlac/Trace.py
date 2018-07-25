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
TraceMap = None
CPUInst = None
DCPUInst = None
CPU_PC = None
DCPU_PC = None


def init(filename, maincpu=None, displaycpu=None):
    """Initialize the trace:

    filename    name of the trace file
    maincpu     the main CPU object (may be added later)
    displaycpu  the display CPU object (may be added later)
    """

    global CPU, DCPU, TraceMap, CPUInst, DCPUInst
    global TraceFile, TraceFilename

    # set internal state
    Tracing = True
    TraceFilename = filename
    try:
        os.remove(filename)
    except:
        pass
    TraceFile = open(filename, 'w')
    TraceFile.write(f"{PYMLAC_VERSION} trace\n{'-'*60}\n")

    CPU = maincpu
    DCPU = displaycpu

    TraceMap = collections.defaultdict(bool)
    log(f'Trace.init: Tracing={Tracing}, TraceFilename={TraceFilename}')

    CPUInst = None
    DCPUInst = None

def start():
    """Prepare trace system for new execution."""

    global CPU_PC, DCPU_PC, CPUInst, DCPUInst

    CPUInst = None
    DCPUInst = None
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

def deimtrace(opcode, code):
    """Trace the DEIM instruction.

    opcode  DEIM opcode
    code    the operation
    """

    log(f"deimtrace: Tracing={Tracing}, writing '{opcode} {code}'")
    if Tracing:
        TraceFile.write('%s\t%s\t' % (opcode, code))
        TraceFile.flush()

def dtrace(ddot, opcode, address=None):
    """Trace the display CPU.

    ddot     address of instruction being traced
    opcode   display opcode
    address  address for the opcode

    Returns the trace string or None if not tracing.
    """

    log(f'Trace.dtrace: Tracing={Tracing}')
    result = None

    if Tracing:
        if address is None:
            result = '%s: %s\t' % (ddot, opcode)
        else:
            result = '%04o: %s\t%5.5o' % (ddot, opcode, address)

    log(f"dtrace: result='{result}'")
    DCPUInst = result
    return result

def itrace(dot, opcode, indirect=False, address=None):
    """Main CPU trace.

    dot       address of instruction being traced
    opcode    the main CPU opcode
    indirect  True if instruction was indirect
    address   address for the instruction (if any)

    Returns the trace string or None if not tracing.
    """

    result = None

    if Tracing and TraceMap[dot]:
        char = '*' if indirect else ''
        if address is None:
            result = '%04o\t%s\t%s' % (dot, opcode, char)
        else:
            result = '%04o\t%s\t%s%5.5o' % (dot, opcode, char, address)

    log(f"itrace: result='{result}'")
    CPUInst = result
    return result

def itraceend(dispon):
    """Trace at the end of one execution cycle.

    dispon  True if the display was on

    Returns the trace string.
    """

    result = ('L=%1.1o AC=%6.6o PC=%6.6o' % (CPU.L, CPU.AC, CPU.PC))

    if dispon:
        result += ' DX=%5.5o DY=%5.5o' % (DCPU.DX, DCPU.DY)

    return result

def end_line():
    """Write the line for this set of I/D instructions."""

    registers = ('L=%1.1o AC=%6.6o PC=%6.6o' % (CPU.L, CPU.AC, CPU.PC))

    if DCPU.Running:
        registers += ' DX=%5.5o DY=%5.5o' % (DCPU.DX, DCPU.DY)

    CPUInst = None
    DCPUInst = None

    #TraceFile.write(f'{CPUInst:-50s}{DCPUInst:-40s}  {registers}\n')
    TraceFile.write('%-50s %-40s  %s\n' % (CPUInst, DCPUInst, registers))

#def flush(self):
#    TraceFile.flush()

def comment(msg):
    """Write a line to the trace file."""

    TraceFile.write(msg + '\n')
    TraceFile.flush()

def settrace(new_tracing):
    """Set the trace ON or OFF."""

    global Tracing

    Tracing = new_tracing
    log(f'Trace.settrace: Tracing={Tracing}')
