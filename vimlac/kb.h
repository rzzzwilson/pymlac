/*
 * Interface for the vimlac KB device (keyboard).
 */

#ifndef KB_H
#define KB_H

void kb_clear_flag(void);
BYTE kb_get_char(void);
bool kb_ready(void);

#endif
