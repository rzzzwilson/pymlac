/*
 * Interface for the imlac TTYOUT (TTY input).
 */

#ifndef TTYOUT_H
#define TTYOUT_H


int ttyout_mount(char *fname);
void ttyout_dismount(void);
void ttyout_send(BYTE value);
void ttyout_clear_flag(void);
bool ttyout_ready(void);
void ttyout_tick(long cycles);


#endif
