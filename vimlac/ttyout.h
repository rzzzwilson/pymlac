/*
 * Interface for the vimlac TTY output device.
 */

#ifndef TTYOUT_H
#define TTYOUT_H

void ttyout_clear_flag(void);
void ttyout_send(BYTE);
bool ttyout_ready(void);

#endif
