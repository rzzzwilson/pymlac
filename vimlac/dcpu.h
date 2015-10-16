/******************************************************************************\
 *                                 dcpu.h                                     *
 *                                --------                                    *
\******************************************************************************/

#ifndef DCPU_H
#define DCPU_H

#include "vimlac.h"

/******
 * Exported functions.
 ******/

void dcpu_start(void);
void dcpu_stop(void);
int dcpu_execute_one(void);
WORD dcpu_get_PC(void);
void dcpu_set_PC(WORD value);
void dcpu_set_DRSindex(int index);
bool dcpu_on(void);


#endif
