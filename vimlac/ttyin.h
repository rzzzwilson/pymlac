/*
 * Interface for the imlac TTYIN (TTY input).
 */

#ifndef TTYIN_H
#define TTYIN_H

int ttyin_mount(char *fname);
void ttyin_dismount(void);
int ttyin_get_char(void);
void ttyin_tick(long cycles);
bool ttyin_ready(void);
void ttyin_clear_flag(void);

#endif
