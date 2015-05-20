// This files holds the code to execute IMLAC main CPU and
// display CPU instructions.

#include <stdio.h>

#include "imlac.h"


// main machine registers
ADDR PC;					// main CPU PC
ADDR AC;					// accumulator
ADDR LINK;					// link register
bool Sync40Hz = 1;          // main CPU 40Hz flag register
ADDR DS;                    // dataswitches value

// display machine registers
ADDR DPC;					// display CPU PC
ADDR DRS[8];				// display CPU ???
ADDR DRSindex;				// display CPU ???
ADDR DIB;					// display CPU ???
ADDR DX;					// display CPU draw X register
ADDR DY;					// display CPU draw Y register


// main CPU implementation stuff
ADDR BlockBase;				// block base address
bool Running;				// true if main CPU is running

// display CPU implementation stuff
DISPLAY_MODE DisplayMode;	// dislay mode, NORMAL or DEIM
bool DRunning;				// true if display CPU is running

// IMLAC memory
int *MEMORY;				// pointer to memory


//-----------------------------------------------------------------------------
// Routines to initialize the IMLAC system
//-----------------------------------------------------------------------------

void
init(ADDR mem_size)
{
	// allocate rquired memory, zero it as well
}

//-----------------------------------------------------------------------------
// Routines to load and save IMLAC memory
//-----------------------------------------------------------------------------

void
load_mem(char *mem_file)
{

}

void
save_mem(char *mem_file)
{

}

//-----------------------------------------------------------------------------
// Routines to set and get IMLAC registers.
//-----------------------------------------------------------------------------

void
set_pc(ADDR value)
{
    PC = value;
}


ADDR
get_pc(void)
{
    return PC;
}


void
set_ac(ADDR value)
{
    AC = value;
}


ADDR
get_ac(void)
{
    return AC;
}


void
set_link(ADDR value)
{
    LINK = value & 0x1;
}


ADDR
get_link(void)
{
    return LINK;
}


//-----------------------------------------------------------------------------
// Execute one or more IMLAC main and display instructions.
//
//    address      address to start executing from
//    num_cycles   number of instructions to execute before returning
//    tracefile    file to trace to (may be NULL)
//    trace        if true do trace immediately
//    trace_start  address to start tracing at
//    trace_end    address to stop tracing at
//-----------------------------------------------------------------------------

void
execute(ADDR address, int num_cycles, FILE *tracefile,
	    bool trace, ADDR trace_start, ADDR trace_end)
{
	int cycles = 0;

	if (!Running && !DRunning)
		return;

	while (cycles < num_cycles)
	{
		int main_cycles;
		int dislay_cycles;

		if (PC == trace_start)
			trace = true;
		else if (PC == trace_stop)
			trace = false;

		main_cycles = execute_main(trace, tracefile);
		display_cycles = execute_display(trace, tracefile);

		cycles += max(display_cycles, main_cycles);

		
	}
// def execute_once():
//     if traceend is None:
//         if MainCPU.PC == tracestart:
//             Trace.settrace(True)
//     else:
//         Trace.settrace(MainCPU.PC >= tracestart and MainCPU.PC <= traceend)

//     if DisplayCPU.ison():
//         Trace.trace('%6.6o' % DisplayCPU.DPC)
//     Trace.trace('\t')

//     instruction_cycles = DisplayCPU.execute_one_instruction()

//     Trace.trace('%6.6o\t' % MainCPU.PC)

//     instruction_cycles += MainCPU.execute_one_instruction()

//     Trace.itraceend(DisplayCPU.ison())

//     __tick_all(instruction_cycles)

//     if not DisplayCPU.ison() and not MainCPU.running:
//         return 0

//     return instruction_cycles
}