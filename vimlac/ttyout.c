/*
 * Implementation for the imlac TTYOUT (TTY output) device.
 */

#include "imlac.h"
#include "ttyout.h"


/*****
 * constants for the TTYOUT device
 *
 * The device reads at 4800 chars/second, so we work out how many imlac
 * machine cycles data is ready/notready at a 30%/70% ready cycle.
 ******/

#define CHARS_PER_SECOND    4800
#define CYCLES_PER_CHAR     (CPU_HERZ / CHARS_PER_SECOND)
#define READY_CYCLES        (int)((3 * CYCLES_PER_CHAR) / 10)
#define NOT_READY_CYCLES    (int)((7 * CYCLES_PER_CHAR) / 10)

#define TTYOUT_EOF           0377

/*****
 * State variables for the TTYOUT device
 ******/

static bool device_ready = false;
static FILE *open_file;
static char *filename = NULL;
static long cycle_count = 0;



/******************************************************************************
Description : Mount a papertape file on the TTYOUT device
 Parameters : fname - pathname of the file to mount
    Returns : 0 if no error, else status code.
   Comments : 
 ******************************************************************************/
int ttyout_mount(char *fname)
{
    filename = fname;
    open_file = fopen(fname, "wb");
    if (open_file == NULL)
    {
        ttyout_dismount();
        return errno;
    }
    device_ready = false;
    cycle_count = NOT_READY_CYCLES;

    return 0;
}


/******************************************************************************
Description : Dismount papertape file from device.
 Parameters : 
    Returns : 
   Comments : Turns motor off.
 ******************************************************************************/
void ttyout_dismount(void)
{
    if (open_file)
        if (fclose(open_file) != 0)
    filename = NULL;
    open_file = NULL;
    device_ready = true;
}


/******************************************************************************
Description : Write a byte value to the device.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void ttyout_send(BYTE value)
{
    if (device_ready)
        fwrite(&value, 1, 1, open_file);
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
void ttyout_clear_flag(void)
{
    device_ready = false;
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
bool ttyout_ready(void)
{
    return device_ready;
}


/******************************************************************************
Description : Tick the state machine along a bit.
 Parameters : cycles - number of imlac cycles that have elapsed
    Returns : 
   Comments : 
 ******************************************************************************/
void ttyout_tick(long cycles)
{
    /* if not open, no state change */
    if (open_file == NULL)
        return;

    /* file mounted */
    cycle_count -= cycles;
    if (cycle_count <= 0L)
    {
        if (device_ready)
        {
            device_ready = false;
            cycle_count += NOT_READY_CYCLES;
        }
        else
        {
            device_ready = true;
            cycle_count += READY_CYCLES;
        }
    }
}
