/*
 * Implementation for the vimlac KB device (keyboard).
 */

#include "vimlac.h"
#include "kb.h"


/*****
 * constants for the KB device
 ******/


/*****
 * State variables for the PTR device
 ******/

static bool flag;	/* true if char ready to read */


void
kb_clear_flag(void)
{
    flag = false;
}


BYTE
kb_get_char(void)
{
    return ' ';
}


bool
kb_ready(void)
{
    return flag;
}


