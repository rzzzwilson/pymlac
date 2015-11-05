/*
 * Implementation for the vimlac PTR/PTP (papertape reader/punch).
 */

#include "vimlac.h"
#include "ptrptp.h"
#include "log.h"


/*****
 * constants for the PTR device
 *
 * The device reads at 300 chars/second, so we work out how many
 * machine cycles data is ready/notready at a 30%/70% ready cycle.
 ******/

#define PTR_CHARS_PER_SECOND        300
#define PTR_CYCLES_PER_CHAR         (CPU_HERZ / PTR_CHARS_PER_SECOND)
#define PTR_READY_CYCLES            (int)((3 * PTR_CYCLES_PER_CHAR) / 10)
#define PTR_NOT_PTR_READY_CYCLES    (int)((7 * PTR_CYCLES_PER_CHAR) / 10)

#define PTR_EOF                     0377

/*****
 * constants for the PTP device
 *
 * The device punches at 30 chars/second, so we work out how many
 * machine cycles device is not ready after punch starts.
 ******/

#define PTP_CHARS_PER_SECOND    30
#define PTP_NOT_READY_CYCLES    (int) (CPU_HERZ / PTP_CHARS_PER_SECOND)

// define some use values
#define InUsePTR "PTR"
#define InUsePTP "PTP"


/*****
 * State variables for the general device
 ******/

static bool device_ready = false;
static char *device_use = NULL;         // NULL, InUsePTR or InUsePTP
static bool device_motor_on = false;
static FILE *device_open_file = NULL;
static char *device_filename = NULL;
static long device_cycle_count = 0;

/*****
 * Specific state variables for the PTR device
 ******/

static bool ptr_at_eof = true;
static BYTE ptr_value = PTR_EOF;


void ptrptp_reset(void)
{
    device_ready = false;
    device_use = NULL;
    device_motor_on = false;
    device_open_file = NULL;
    device_filename = NULL;
    device_cycle_count = 0;
}


int
ptr_mount(char *fname)
{
    if (STREQ(device_use, InUsePTP))
       error("ptr_mount: Can't mount PTR file, being used as PTP");

    device_filename = fname;
    device_open_file = fopen(fname, "rb");
    if (device_open_file == NULL)
    {
        ptr_dismount();
        error("ptr_mount: can't mount file %s", fname);
    }
    device_motor_on = false;
    device_ready = false;
    ptr_at_eof = false;
    ptr_value = PTR_EOF;
    device_cycle_count = PTR_NOT_PTR_READY_CYCLES;
    device_use = InUsePTR;

    return 0;
}


void
ptr_dismount(void)
{
    if (STREQ(device_use, InUsePTP))
       error("ptr_mount: Can't dismount PTR file, being used as PTP");

    if (device_open_file)
        fclose(device_open_file);
    device_filename = NULL;
    device_open_file = NULL;
    device_motor_on = false;
    device_ready = false;
    ptr_at_eof = true;
    ptr_value = PTR_EOF;
    device_use = NULL;
}


void
ptr_start(void)
{
    if (STREQ(device_use, InUsePTP))
       error("ptrptp_start: Can't start PTR motor, being used as PTP, device_use=%s", device_use);

    device_motor_on = true;
    device_ready = false;
    device_cycle_count = PTR_NOT_PTR_READY_CYCLES;
}


void
ptr_stop(void)
{
    if (STREQ(device_use, InUsePTP))
       error("ptr_stop: Can't stop PTR motor, being used as PTP");

    device_motor_on = false;
    device_cycle_count = PTR_NOT_PTR_READY_CYCLES;
    device_ready = false;
}


int
ptr_read(void)
{
    if (STREQ(device_use, InUsePTP))
        error("ptr_read: Can't read PTR, device being used as PTP");

    return ptr_value;
}


bool
ptr_ready(void)
{
    return device_ready;
}


void
ptr_tick(long cycles)
{
    // if not being used as PTR, do nothing
    if (STREQ(device_use, InUsePTP))
        return;

    /* if no state change */
    if (!device_motor_on || ptr_at_eof || device_open_file == NULL)
        return;

    /* tape in, motor on */
    device_cycle_count -= cycles;
    if (device_cycle_count <= 0L)
    {
        if (device_ready == true)
        {
            device_ready = false;
            device_cycle_count += PTR_NOT_PTR_READY_CYCLES;
        }
        else
        {
            device_ready = true;
            device_cycle_count += PTR_READY_CYCLES;
            if (fread(&ptr_value, sizeof(BYTE), 1, device_open_file) != 1)
            {   /* EOF on file */
                ptr_at_eof = true;
                ptr_value = PTR_EOF;
            }
        }
    }
}

// MID

int
ptp_mount(char *fname)
{
    if (STREQ(device_use, InUsePTR))
        error("ptp_mount: Can't mount PTP, device being used as '%s'", device_use);

    device_use = InUsePTP;
    device_filename = fname;
    device_open_file = fopen(fname, "wb");
    if (device_open_file == NULL)
    {
        ptp_dismount();
        error("ptp_mount: Can't mount file %s", fname);
    }
    device_motor_on = false;
    device_ready = false;
    device_cycle_count = PTP_NOT_READY_CYCLES;

    return 0;
}


void
ptp_dismount(void)
{
    if (STREQ(device_use, InUsePTR))
       error("ptp_dismount: Can't dismount PTP, device being used as PTR");

    if (device_open_file)
        if (fclose(device_open_file) != 0)
    device_filename = NULL;
    device_open_file = NULL;
    device_motor_on = false;
    device_ready = true;
}


void
ptp_start(void)
{
    if (STREQ(device_use, InUsePTR))
       error("ptp_dismount: Can't start PTP, device being used as PTR");

    device_motor_on = true;
    device_ready = false;
    device_cycle_count = PTP_NOT_READY_CYCLES;
}


void
ptp_stop(void)
{
    if (STREQ(device_use, InUsePTR))
       error("ptp_stop: Can't stop PTP, device being used as PTR");

    device_motor_on = false;
    device_cycle_count = PTP_NOT_READY_CYCLES;
}


void
ptp_punch(BYTE value)
{
    if (STREQ(device_use, InUsePTR))
       error("ptp_punch: Can't punch PTP, device being used as PTR");

    if (device_motor_on && device_open_file != NULL)
    {
        putc(value, device_open_file);
        device_cycle_count = PTP_NOT_READY_CYCLES;
    }
}


bool
ptp_ready(void)
{
    return device_ready;
}


void
ptp_tick(long cycles)
{
    if (STREQ(device_use, InUsePTR))
       return;

    /* if no mounted file */
    if (device_open_file == NULL)
        return;

    /* tape in */
    device_cycle_count -= cycles;
    if (device_cycle_count <= 0L)
    {
        if (!device_ready)
            device_ready = true;
        device_cycle_count = 0;
    }
}
