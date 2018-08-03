/*
 * Interface for the vimlac display.
 *
 * This interface is used by all the display backends:
 *     PBM
 *     SDL
 */

#ifndef DISPLAY_H
#define DISPLAY_H

#include "vimlac.h"


bool display_init(void);
void display_draw(int x1, int y1, int x2, int y2);
void display_reset(void);
void display_write(void);
void display_close(void);
bool display_dirty(void);


#endif

