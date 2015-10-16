/*
 * Interface for the vimlac TTY input device.
 */

#ifndef TTYIN_H
#define TTYIN_H

void ttyin_clear_flag(void);
BYTE ttyin_get_char(void);
bool ttyin_ready(void);

#endif
