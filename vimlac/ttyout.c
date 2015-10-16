/*
 * Implementation for the vimlac TTY output device.
 */

#include "vimlac.h"
#include "ttyout.h"


/*****
 * constants for the TTYOUT device
 ******/


/*****
 * State variables for the TTYOUT device
 ******/

static bool flag;	/* true if char ready to read */


void
ttyout_clear_flag(void)
{
    flag = false;
}


void
ttyout_send(BYTE ch)
{
    return;
}


bool
ttyout_ready(void)
{
    return flag;
}


