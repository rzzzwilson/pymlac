/*
 * Implementation for the vimlac TTY input device.
 */

#include "vimlac.h"
#include "ttyin.h"


/*****
 * constants for the TTYIN device
 ******/


/*****
 * State variables for the TTYIN device
 ******/

static bool flag;	/* true if char ready to read */


void
ttyin_clear_flag(void)
{
    flag = false;
}


BYTE
ttyin_get_char(void)
{
    return ' ';
}


bool
ttyin_ready(void)
{
    return flag;
}


