/******************************************************************************\
 *                                dcpu.c                                      *
 *                                -------                                     *
 *                                                                            *
 *  This file is used to decode and execute a display processor instruction.  *
 *                                                                            *
\******************************************************************************/

#include "vimlac.h"
#include "dcpu.h"
#include "memory.h"


/******
 * Emulated registers, state, memory, etc.
 ******/

static WORD     r_PC;
static WORD	Prev_r_PC;
static int	r_DRSindex;


/******
 * Environment stuff.  PTR and TTY in and out files, etc
 ******/

static bool	cpu_is_on;	/* true if display processor is running */


/******************************************************************************
Description : Functions to get/set various registers.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
WORD
dcpu_get_PC(void)
{
    return r_PC;
}


void
dcpu_set_PC(WORD value)
{
    r_PC = value;
}


void
dcpu_set_DRSindex(int value)
{
    r_DRSindex = value;
}


/******************************************************************************
Description : Function to handle unrecognized instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static void
illegal(void)
{
    WORD oldPC = Prev_r_PC & MEMMASK;

/*    memdump(LogOut, oldPC - 8, 16); */

    error("INTERNAL ERROR: "
          "unexpected main processor opcode %06.6o at address %06.6o",
          mem_get(oldPC, false), oldPC);
}


/******************************************************************************
Description : Function to execute one display processor instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int
dcpu_execute_one(void)
{
    WORD instruction = 0;
    bool indirect = false;
    WORD opcode = 0;
    WORD address = 0;

/******
 * If processor not running, return immediately.
 ******/

    if (!cpu_is_on)
        return 0;

/******
 * Fetch the instruction.  Split into initial opcode and address.
 ******/

    Prev_r_PC = r_PC;
    instruction = mem_get(r_PC++, false);
    r_PC = r_PC & MEMMASK;

    indirect = (bool) (instruction & 0100000);	/* high bit set? */
    opcode = (instruction >> 11) & 017;		/* high 5 bits */
    address = instruction & 03777;		/* low 11 bits */

/******
 * Now decode it.
 ******/

#ifdef JUNK
    switch (opcode)
    {
    }
#endif
    ++instruction;
    indirect = !indirect;
    ++opcode;
    ++address;
    illegal();

    return 0;
}


/******************************************************************************
Description : Function to get CPU state.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
bool
dcpu_on(void)
{
    return cpu_is_on;
}


/******************************************************************************
Description : Function to start the CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_start(void)
{
    cpu_is_on = true;
}


/******************************************************************************
Description : Function to stop the CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_stop(void)
{
    cpu_is_on = false;
}


/******************************************************************************
Description : Function to stop the CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_set_drsindex(int index)
{
    r_DRSindex = index;
}


