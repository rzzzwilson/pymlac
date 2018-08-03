/*
 * A display object that write *.PBM files.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "vimlac.h"
#include "display.h"
#include "dcpu.h"
#include "log.h"


/*****
 * constants for the display device
 ******/

#define PBM_EXTENSION               "pbm"
#define SCALE_MAX_X                 2048
#define SCALE_MAX_Y                 2048


/*****
 * State variables for the display
 ******/

static BYTE *pbm_display;          // pointer to display array of chars
static bool pbm_running = false;   // true if display is ON
static int pbm_cyclecount = 0;     // number of cycles for one instruction execution
static int pbm_sync40 = 0;         // counter for 40Hz flag
static int pbm_file_num = 0;       // number of next PBM file to write
static bool pbm_dirty = false;     // 'true' if buffer unsaved


bool
display_dirty(void)
{
    return pbm_dirty;
}


void
display_reset(void)
{
    for (int i = 0; i < SCALE_MAX_X * SCALE_MAX_Y; ++i)
        pbm_display[i] = 1;
    vlog("Max display cell is at %d", SCALE_MAX_X * SCALE_MAX_Y -1);

    // set internal state
    pbm_running = 0;
    pbm_cyclecount = 0;
    pbm_sync40 = 1;
    pbm_file_num = 0;
    pbm_dirty = false;
}


bool
display_init(void)
{
    pbm_display = malloc(sizeof(BYTE) * SCALE_MAX_X * SCALE_MAX_Y);
    if (!pbm_display)
    {
        printf("Out of memory in 'display_init()'!?\n");
        return false;
    }

    display_reset();

    vlog("display_init: done");

    return true;
}

void
display_write(void)
{
    if (!pbm_dirty)
        return;

    vlog("display_write: writing!");

    char fname[1024];

    pbm_file_num += 1;
    sprintf(fname, "pymlac_%06d.pbm", pbm_file_num);
    printf("fname=%s", fname);
    FILE *fd = fopen(fname, "w");
    fprintf(fd, "P1\n");
    fprintf(fd, "# created by pymlac %s\n", VIMLAC_VERSION);
    fprintf(fd, "%d %d\n", SCALE_MAX_X, SCALE_MAX_Y);
    for (int i = 0; i < SCALE_MAX_X * SCALE_MAX_Y; ++i)
    {
        fprintf(fd, "%d\n", pbm_display[i]);
    }
    fclose(fd);

    pbm_dirty = false;

    vlog("display_write: done");
}


//*********************************************************
// Draw a line on the screen.
//
//     x1, y1  start coordinates
//     x2, y2  end coordinates
//     dotted  True if dotted line, else False (IGNORED)
//
// Algorithm from:
//     http://csourcecodes.blogspot.com/2016/06/bresenhams-line-drawing-algorithm-generalized-c-program.html
//*********************************************************
//
void
//draw(int x1, int y1, int x2, int y2, dotted=False)
display_draw(int x1, int y1, int x2, int y2)
{
    vlog("display_draw: x1=%d, y1=%d, x2=%d, y2=%d", x1, y1, x2, y2);

    // invert the Y axes
    y1 = SCALE_MAX_Y - 1 - y1;
    y2 = SCALE_MAX_Y - 1 - y2;

    // draw the line (Bresenham algorithm)
    int x = x1;
    int y = y1;
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int s1 = 0;
    int s2 = 0;
    if (x2 > x1)
        s1 = 1;
    if (x2 < x1)
        s1 = -1;
    if (y2 > y1)
        s2 = 1;
    if (y2 < y1)
        s2 = -1;

    bool swap = false;
    if (dy > dx)
    {
        int temp = dx;

        dx = dy;
        dy = temp;
        swap = true;
    }
    int p = 2*dy - dx;
    for (int i = 0; i < dx;  ++i)
    {
        vlog("display_draw: setting pixel (%d,%d)", x, y);
//        pbm_display[y*SCALE_MAX_X + x] = 0;
        pbm_display[y*SCALE_MAX_X + x] = 0;
        while (p >= 0)
        {
            p = p - 2*dx;
            if (swap)
                x += s1;
            else
                y += s2;
        }
        p = p + 2*dy;
        if (swap)
            y += s2;
        else
            x += s1;
    }

    // draw the final point
    vlog("display_draw: setting pixel (%d,%d)", x, y);
//    pbm_display[y*SCALE_MAX_X + x] = 0;
    pbm_display[y*SCALE_MAX_X + x] = 0;

    pbm_dirty = true;

    vlog("display_draw: finished");
}


void
display_clear(void)
{
    // clear display, but write display to next PBM file first
    if (pbm_dirty)
        display_write();
    display_reset();
}


void
display_close(void)
{
    if (pbm_dirty)
        display_write();
    free(pbm_display);
}
