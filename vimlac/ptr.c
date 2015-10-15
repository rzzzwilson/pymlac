/*
 * Implementation for the imlac PTR (papertape reader) device.
 */

#include "imlac.h"
#include "ptr.h"


/*****
 * constants for the PTR device
 *
 * The device reads at 300 chars/second, so we work out how many imlac
 * machine cycles data is ready/notready at a 30%/70% ready cycle.
 ******/

#define CHARS_PER_SECOND    300
#define CYCLES_PER_CHAR     (CPU_HERZ / CHARS_PER_SECOND)
#define READY_CYCLES        (int)((3 * CYCLES_PER_CHAR) / 10)
#define NOT_READY_CYCLES    (int)((7 * CYCLES_PER_CHAR) / 10)

#define PTR_EOF             0377

/*****
 * State variables for the PTR device
 ******/

static bool motor_on = false;
static bool device_ready = false;
static FILE *open_file;
static char *filename = NULL;
static bool at_eof = false;
static BYTE value = PTR_EOF;
static long cycle_count = 0;



/******************************************************************************
Description : Mount a papertape file on the PTR device
 Parameters : fname - pathname of the file to mount
    Returns : 0 if no error, else status code.
   Comments : 
 ******************************************************************************/
int ptr_mount(char *fname)
{
    filename = fname;
    open_file = fopen(fname, "rb");
    if (open_file == NULL)
    {
        ptr_dismount();
        return errno;
    }
    motor_on = false;
    device_ready = false;
    at_eof = false;
    value = PTR_EOF;
    cycle_count = NOT_READY_CYCLES;

    return 0;
}


/******************************************************************************
Description : Dismount papertape file from device.
 Parameters : 
    Returns : 
   Comments : Turns motor off.
 ******************************************************************************/
void ptr_dismount(void)
{
    if (open_file)
        if (fclose(open_file) != 0)
    filename = NULL;
    open_file = NULL;
    motor_on = false;
    device_ready = true;
    at_eof = true;
    value = PTR_EOF;
}


/******************************************************************************
Description : Start the papertape device motor.
 Parameters : 
    Returns : 
   Comments : We don't check if papertape mounted as the real imlac doesn't.
 ******************************************************************************/
void ptr_start(void)
{
    motor_on = true;
    device_ready = false;
    cycle_count = NOT_READY_CYCLES;
}


/******************************************************************************
Description : Turn the papertape device motor off.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void ptr_stop(void)
{
    motor_on = false;
    cycle_count = NOT_READY_CYCLES;
}


/******************************************************************************
Description : Read the current value of the papertape device.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int ptr_read(void)
{
    return value;
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
bool ptr_ready(void)
{
    return device_ready;
}


/******************************************************************************
Description : Tick the state machine along a bit.
 Parameters : cycles - number of imlac cycles that have elapsed
    Returns : 
   Comments : 
 ******************************************************************************/
void ptr_tick(long cycles)
{
    /* if no state change */
    if (!motor_on || at_eof || open_file == NULL)
        return;

    /* tape in, motor on */
    cycle_count -= cycles;
    if (cycle_count <= 0L)
    {
        if (device_ready)
        {
            device_ready = false;
            cycle_count += NOT_READY_CYCLES;
	    value = 0;
        }
        else
        {
            device_ready = true;
            cycle_count += READY_CYCLES;
            if (fread(&value, sizeof(BYTE), 1, open_file) != 1)
            {   /* assume EOF on file, dismount tape */
		fclose(open_file);
		open_file = NULL;
                at_eof = true;
                value = PTR_EOF;
            }
        }
    }
}
