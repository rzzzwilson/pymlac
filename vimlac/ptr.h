/*
 * Interface for the vimlac PTR (papertape reader).
 */

#ifndef PTR_H
#define PTR_H

int ptr_mount(char *fname);
void ptr_dismount(void);
void ptr_start(void);
void ptr_stop(void);
int ptr_read(void);
void ptr_tick(long cycles);
bool ptr_ready(void);

#endif
