/******************************************************************************\
 *                                 dcpu.h                                     *
 *                                --------                                    *
\******************************************************************************/

#ifndef DCPU_H
#define DCPU_H

//#include "vimlac.h"

WORD dcpu_get_PC(void);
void dcpu_set_PC(WORD value);
void dcpu_set_DRSindex(int value);
int dcpu_execute_one(void);
bool dcpu_running(void);
void dcpu_start(void);
void dcpu_stop(void);
void dcpu_set_drsindex(int index);
int dcpu_get_x(void);
int dcpu_get_y(void);

#endif
