/******************************************************************************\
 *                                  dcpu.h                                    *
 *                                 --------                                   *
 *                                                                            *
 *  Implements all display CPU instructions.                                  *
 *                                                                            *
\******************************************************************************/

#ifndef DCPU_H
#define DCPU_H

#include "imlac.h"

/******
 * Exported functions.
 ******/

bool dcpu_running(void);
void dcpu_start(void);
void dcpu_stop(void);
void dcpu_set_DRSindex(WORD);
int dcpu_execute_one(void);
WORD dcpu_get_AC(void);
WORD dcpu_get_DPC(void);
WORD dcpu_get_prev_DPC(void);
void dcpu_set_DPC(WORD dpc);

#endif
