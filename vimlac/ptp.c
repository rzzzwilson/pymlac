/*
 * Implementation for the imlac PTP (papertape punch) device.
 */

#include "imlac.h"
#include "ptp.h"


/*****
 * constants for the PTP device
 *
 * The device punches at 100 chars/second, so we work out how many imlac
 * machine cycles data is ready/notready at a 30%/70% ready cycle.
 ******/

#define CHARS_PER_SECOND    100
#define CYCLES_PER_CHAR     (CPU_HERZ / CHARS_PER_SECOND)
#define READY_CYCLES        (int)((3 * CYCLES_PER_CHAR) / 10)
#define NOT_READY_CYCLES    (int)((7 * CYCLES_PER_CHAR) / 10)

/*****
 * State variables for the PTP device
 ******/

static bool motor_on = false;
static bool device_ready = false;
static FILE *open_file;
static char *filename = NULL;
static long cycle_count = 0;
static char value = 0;



/******************************************************************************
Description : Mount a papertape file on the PTP device
 Parameters : fname - pathname of the file to mount
    Returns : 0 if no error, else status code.
   Comments : 
 ******************************************************************************/
int ptp_mount(char *fname)
{
    filename = fname;
    open_file = fopen(fname, "wb");
    if (open_file == NULL)
    {
        ptp_dismount();
        return errno;
    }
    motor_on = false;
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
void ptp_dismount(void)
{
    if (open_file)
        if (fclose(open_file) != 0)
    filename = NULL;
    open_file = NULL;
    motor_on = false;
    device_ready = false;
}


/******************************************************************************
Description : Start the papertape device motor.
 Parameters : 
    Returns : 
   Comments : We don't check if papertape mounted as the real imlac doesn't.
 ******************************************************************************/
void ptp_start(void)
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
void ptp_stop(void)
{
    motor_on = false;
    device_ready = false;
    cycle_count = NOT_READY_CYCLES;
}


/******************************************************************************
Description : Write the current value to the papertape punch file.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int ptp_punch(BYTE value)
{
    return value;
}


/******************************************************************************
Description : Get the papertape device status.
 Parameters : 
    Returns : TRUE if device ready, else FALSE.
   Comments : 
 ******************************************************************************/
bool ptp_ready(void)
{
    return device_ready;
}


/******************************************************************************
Description : Tick the state machine along a bit.
 Parameters : cycles - number of imlac cycles that have elapsed
    Returns : 
   Comments : 
 ******************************************************************************/
void ptp_tick(long cycles)
{
    /* if no state change */
    if (!motor_on || open_file == NULL)
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
            }
        }
    }
}
