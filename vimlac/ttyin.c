/*
 * Implementation for the imlac TTYIN (TTY input) device.
 */

#include "imlac.h"
#include "ttyin.h"


/*****
 * constants for the TTYIN device
 *
 * The device reads at 4800 chars/second, so we work out how many imlac
 * machine cycles data is ready/notready at a 30%/70% ready cycle.
 ******/

#define CHARS_PER_SECOND    4800
#define CYCLES_PER_CHAR     (CPU_HERZ / CHARS_PER_SECOND)
#define READY_CYCLES        (int)((3 * CYCLES_PER_CHAR) / 10)
#define NOT_READY_CYCLES    (int)((7 * CYCLES_PER_CHAR) / 10)

#define TTYIN_EOF           0377

/*****
 * State variables for the TTYIN device
 ******/

static bool device_ready = false;
static FILE *open_file;
static char *filename = NULL;
static bool at_eof = false;
static BYTE value = TTYIN_EOF;
static long cycle_count = 0;



/******************************************************************************
Description : Mount a papertape file on the TTYIN device
 Parameters : fname - pathname of the file to mount
    Returns : 0 if no error, else status code.
   Comments : 
 ******************************************************************************/
int ttyin_mount(char *fname)
{
    filename = fname;
    open_file = fopen(fname, "rb");
    if (open_file == NULL)
    {
        ttyin_dismount();
        return errno;
    }
    device_ready = false;
    at_eof = false;
    value = TTYIN_EOF;
    cycle_count = NOT_READY_CYCLES;

    return 0;
}


/******************************************************************************
Description : Dismount papertape file from device.
 Parameters : 
    Returns : 
   Comments : Turns motor off.
 ******************************************************************************/
void ttyin_dismount(void)
{
    if (open_file)
        if (fclose(open_file) != 0)
    filename = NULL;
    open_file = NULL;
    device_ready = true;
    at_eof = true;
    value = TTYIN_EOF;
}


/******************************************************************************
Description : Read the current value of the papertape device.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int ttyin_get_char(void)
{
    return value;
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
void ttyin_clear_flag(void)
{
    device_ready = false;
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
bool ttyin_ready(void)
{
    return device_ready;
}


/******************************************************************************
Description : Tick the state machine along a bit.
 Parameters : cycles - number of imlac cycles that have elapsed
    Returns : 
   Comments : 
 ******************************************************************************/
void ttyin_tick(long cycles)
{
    /* if no state change */
    if (at_eof || open_file == NULL)
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
                value = TTYIN_EOF;
            }
        }
    }
}
