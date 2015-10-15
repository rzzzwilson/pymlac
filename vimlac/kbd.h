/******************************************************************************\
 *                                  kbd.h                                     *
 *                                 -------                                    *
 *                                                                            *
 *  Implements all display CPU instructions.                                  *
 *                                                                            *
\******************************************************************************/

#ifndef KBD_H
#define KBD_H

#include "imlac.h"

/******
 * Exported functions.
 ******/


void kbd_clear_flag(void);
WORD kbd_get_char(void);
bool kbd_ready(void);


#endif
