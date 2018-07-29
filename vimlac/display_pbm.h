/*
 * Interface for the vimlac PBM display.
 */

#ifndef DISPLAY_PBM_H
#define DISPLAY_PBM_H


void display_reset(void);
void display_init(void);
void display_write(void);
void display_draw(int x1, int y1, int x2, int y2);
void display_clear(void);
void display_close(void);
bool display_dirty(void);


#endif
