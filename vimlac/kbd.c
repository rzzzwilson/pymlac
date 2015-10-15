/******************************************************************************\
 *                                 kbd.c                                      *
 *                                -------                                     *
 *                                                                            *
 *  This file is used to implement a KBD device (keyboard).                   *
 *                                                                            *
\******************************************************************************/

#include "imlac.h"
#include "kbd.h"
#include "trace.h"


/******
 * Emulated registers, state, memory, etc.
 ******/

static WORD     state_KBD;
static bool     clear = false;


/******************************************************************************
Description : Clear the KBD (keyboard) flag.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
kbd_clear_flag(void)
{
    clear = false;
}

/******************************************************************************
Description : Get the character in the keyboard buffer.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
WORD
kbd_get_char(void)
{
    return 'a';
}

/******************************************************************************
Description : Test if the keyboard is ready with the next character.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
bool
kbd_ready(void)
{
    return !clear;
}


