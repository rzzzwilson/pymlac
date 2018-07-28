/*
 * A display object that write *.PBM files.
 */

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "vimlac.h"
#include "display_pbm.h"
#include "log.h"


/*****
 * constants for the display device
 ******/

#define PBM_EXTENSION               "pbm"
#define SCALE_MAX_X                 1024
#define SCALE_MAX_Y                 1024


/*****
 * State variables for the display
 ******/

static char *pbm_display;          // pointer to display array of chars
static bool pbm_running = false;   // true if display is ON
static int pbm_cyclecount = 0;     // number of cycles for one instruction execution
static int pbm_sync40 = 0;         // counter for 40Hz flag
static int pbm_file_num = 0;       // number of next PBM file to write
static bool pbm_dirty = false;     // 'true' if buffer unsaved

void
display_reset(void)
{
    for (int i = 0; i < SCALE_MAX_X * SCALE_MAX_Y; ++i)
        pbm_display[i] = 0;

    // set internal state
    pbm_running = 0;
    pbm_cyclecount = 0;
    pbm_sync40 = 1;
    pbm_file_num = 0;
    pbm_dirty = false;
}


void
display_init(void)
{
    pbm_display = (char *) malloc(sizeof(bool) * SCALE_MAX_X * SCALE_MAX_Y);
    display_reset();
}

void
display_write(void)
{
    char fname[1024];

    pbm_file_num += 1;
    sprintf(fname, "pymlac_%06d.pbm", pbm_file_num);
    printf("fname=%s", fname);
    FILE *fd = fopen(fname, "w");
    fprintf(fd, "P1\n");
    fprintf(fd, "# created by pymlac %s\n", VIMLAC_VERSION);
    fprintf(fd, "%d %d\n", SCALE_MAX_X, SCALE_MAX_Y);
    for (int i = 0; i < SCALE_MAX_X * SCALE_MAX_Y; ++i)
        fprintf(fd, "%d\n", pbm_display[i]);
    fclose(fd);

    pbm_dirty = false;
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
    // convert virtual coords to physical
    x1 /= 2;
    y1 /= 2;
    x2 /= 2;
    y2 /= 2;

    // invert the Y axis
    y1 = SCALE_MAX_Y - y1;
    y2 = SCALE_MAX_Y - y2;

    // draw the line (Bresenham algorithm)
    int x = x1;
    int y = y1;
    int dx = abs(x2 - x1);
    int dy = abs(y2 - y1);
    int s1, s2;
    if (x2 > x1)
        s1 = 1;
    else
        s2 = -1;
    if (y2 > y1)
        s2 = 1;
    else
        s2 = -1;
    bool swap = false;
    pbm_display[(y-1)*SCALE_MAX_X + x - 1] = 1;
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
        pbm_display[(y-1)*SCALE_MAX_X + x - 1] = 1 ;
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

    pbm_dirty = true;
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
