/*
 * Implementation for the vimlac PTP (papertape punch).
 */

#include "vimlac.h"
#include "ptp.h"


/*****
 * constants for the PTP device
 *
 * The device punches at 300 chars/second, so we work out how many
 * machine cycles device is not ready after punch starts.
 ******/

#define CHARS_PER_SECOND    300
#define NOT_READY_CYCLES    (int) (CPU_HERZ / CHARS_PER_SECOND)

/*****
 * State variables for the PTR device
 ******/

static bool motor_on = false;
static bool device_ready = false;
static FILE *open_file;
static char *filename = NULL;
static long cycle_count = 0;


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


void ptp_dismount(void)
{
    if (open_file)
        if (fclose(open_file) != 0)
    filename = NULL;
    open_file = NULL;
    motor_on = false;
    device_ready = true;
}


void ptp_start(void)
{
    motor_on = true;
    device_ready = false;
    cycle_count = NOT_READY_CYCLES;
}


void ptp_stop(void)
{
    motor_on = false;
    cycle_count = NOT_READY_CYCLES;
}


void ptp_punch(BYTE value)
{
    if (motor_on && open_file != NULL)
    {
        putc(value, open_file);
        cycle_count = NOT_READY_CYCLES;
    }
}


bool ptp_ready(void)
{
    return device_ready;
}


void ptp_tick(long cycles)
{
    /* if no state change */
    if (!motor_on || open_file == NULL)
        return;

    /* tape in, motor on */
    cycle_count -= cycles;
    if (cycle_count <= 0L)
    {
        if (!device_ready)
            device_ready = true;
        cycle_count = 0;
    }
}
