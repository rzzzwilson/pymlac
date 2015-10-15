/******************************************************************************\
 *                                 dcpu.c                                     *
 *                                --------                                    *
 *                                                                            *
 *  This file is used to decode and execute a display processor instruction.  *
 *                                                                            *
\******************************************************************************/

#include "imlac.h"
#include "dcpu.h"
#include "memory.h"
#include "trace.h"


/******
 * Emulated registers, state, memory, etc.
 ******/

static WORD     r_DPC;
static WORD     Prev_r_DPC;
static WORD     DRSindex = 0;

/* 40Hz sync stuff */
static bool            Sync40HzOn = false;

/******
 * Environment stuff.  PTR and TTY in and out files, etc
 ******/

static bool            dcpu_on;       /* true if display processor is running */
static bool            dcpu_sync_on;  /* true if 40HZ flag set */


/******************************************************************************
Description : Function to get the display CPU status.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
bool
dcpu_running(void)
{
    return dcpu_on == true;
}


/******************************************************************************
Description : Function to start the display CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_start(void)
{
    dcpu_on = true;
}


/******************************************************************************
Description : Function to stop the display CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_stop(void)
{
    dcpu_on = false;
}


/******************************************************************************
Description : Functions to get various registers.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
WORD
dcpu_get_DPC(void)
{
    return r_DPC;
}


WORD
dcpu_get_prev_DPC(void)
{
    return Prev_r_DPC;
}


void
dcpu_set_DPC(WORD new_dpc)
{
    r_DPC = new_dpc;
}

void
dcpu_set_DRSindex(WORD drsindex)
{
    DRSindex = drsindex;
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
    WORD oldDPC = Prev_r_DPC & MEMMASK;

    error("INTERNAL ERROR: "
          "unexpected display processor opcode %06.6o at address %06.6o",
          mem_get(oldDPC, false), oldDPC);
}


/******************************************************************************
Description : 
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_LAW_LWC(bool indirect, WORD address)
{
    return 1;
}


/******************************************************************************
Description : Function to execute one display processor instruction.
 Parameters : 
    Returns : The number of cycles the instruction took.
   Comments : 
 ******************************************************************************/
int
dcpu_execute_one(void)
{
    WORD instruction;
    WORD opcode;
    WORD address;
    bool indirect;

/******
 * If main processor not running, return immediately.
 ******/

    if (!dcpu_on)
        return 0;

/******
 * Fetch the instruction.  Split into initial opcode and address.
 ******/

    Prev_r_DPC = r_DPC;
    instruction = mem_get(r_DPC++, false);
    r_DPC = r_DPC & MEMMASK;

    indirect = (bool) (instruction & 0100000);	/* high bit set? */
    opcode = (instruction >> 11) & 017;		/* high 5 bits */
    address = instruction & 03777;		/* low 11 bits */

/******
 * Now decode it.
 ******/

    switch (opcode)
    {
	default: illegal();
    }

    return 0;	/* CAN'T REACH */
}


