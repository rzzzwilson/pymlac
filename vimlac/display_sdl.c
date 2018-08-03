/******************************************************************************\
 *                             display_sdl.c                                  *
 *                             -------------                                  *
 *                                                                            *
 *  This file is used to display the vimlac screen using the SDL2 library.    *
 *                                                                            *
 *  TODO: make display size dynamic depending on screen size, ie, choose one  *
 *        (51, 512), (1024, 1024) or (2048, 2048).                            *
 *                                                                            *
\******************************************************************************/

#include <SDL.h>
#include "display.h"


/******
 * Constants, etc.
 ******/

#define MAX_X           512     // max X coord
#define MAX_Y           512     // max Y coord
#define DL_INIT_SIZE    2048    // initial size of the DisplayList array
#define DL_INC_SIZE     1024    // how much we increase DisplayList size

// struct to hold info for one line drawn from (x1,y1) to (x2,y2)
typedef struct DrawLine
{
   int x1;
   int y1;
   int x2;
   int y2;
} DrawLine;

// display state variables
static SDL_Window* window = NULL;       // the SDL window reference
static SDL_Renderer* renderer = NULL;   // reference to SDL renderer

static DrawLine *DisplayList;           // the DrawLine array
static int DisplayListSize = 0;         // current size of the dynamic DisplayList
static int NumLines = 0;                // number of lines in DisplayList
static bool DisplayDirty = false;       // true if the DisplayList has changed


/******************************************************************************
Description : Draw one line on the vimlac screen.
 Parameters : x1, y1 - start point coordinates
            : x2, y2 - stop point coordinates
    Returns : 
   Comments : Must check if DisplayList full and reallocate it bigger.
 ******************************************************************************/

void display_draw(int x1, int y1, int x2, int y2)
{
    // check if DisplayList full
    if (NumLines >= DisplayListSize)
    {
        int newsize = DisplayListSize + DL_INC_SIZE;

        DisplayList = realloc(DisplayList, sizeof(DrawLine) * newsize);
        if (!DisplayList)
        {
            printf("Out of memory in 'display_draw()' reallocing to %d bytes.\n",
                   newsize);
            printf("Possibly runaway display processor!?\n");
            display_close();
            exit(1);
        }

        DisplayListSize = newsize;
    }

    // add new line to DisplayList
    DrawLine *p = &DisplayList[NumLines++];

    p->x1 = x1;
    p->y1 = y1;
    p->x2 = x2;
    p->y2 = y2;

    DisplayDirty = true;
}


/******************************************************************************
Description : Draw the DisplayList to the SDL screen.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/

void display_write(void)
{
    DrawLine *p = DisplayList;    // get pointer to first struct in DisplayList

    SDL_SetRenderDrawColor(renderer, 0, 0, 0, SDL_ALPHA_OPAQUE);
    SDL_RenderClear(renderer);
    SDL_SetRenderDrawColor(renderer, 255, 255, 255, SDL_ALPHA_OPAQUE);

    for (int i = 0; i < NumLines; ++i)
    {
        SDL_RenderDrawLine(renderer, p->x1, p->y1, p->x2, p->y2);
        ++p;
    }

    SDL_RenderPresent(renderer);

    DisplayDirty = false;
}


/******************************************************************************
Description : Set the state back to "nothing on the screen".
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/

void display_reset(void)
{
    NumLines = 0;
    DisplayDirty = true;
}


/******************************************************************************
Description : Initialize the SDL system.
 Parameters : 
    Returns : 'true' if all went well, else 'false'.
   Comments : 
 ******************************************************************************/

bool display_init()
{
    if (SDL_Init(SDL_INIT_VIDEO) != 0)
        return false;

    if (SDL_CreateWindowAndRenderer(MAX_X, MAX_Y, 0, &window, &renderer) != 0)
    {
        if (renderer)
            SDL_DestroyRenderer(renderer);
        if (window)
            SDL_DestroyWindow(window);
        return false;
    }

    // allocate the initial DisplayList array
    DisplayList = malloc(sizeof(DrawLine) * DL_INIT_SIZE);
    if (DisplayList)
    {
        DisplayListSize = DL_INIT_SIZE;
        display_reset();
        return true;
    }

    // error allocating DisplayList if we get here
    // free up DSL resources
    display_close();
    return false;
}


/******************************************************************************
Description : Get the display "dirty" flag.
 Parameters : 
    Returns : 'true' if the DisplayList has changed, else 'false'.
   Comments : 
 ******************************************************************************/

bool display_dirty(void)
{
    return DisplayDirty;
}


/******************************************************************************
Description : Close down the SDL system.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/

void display_close(void)
{
    if (renderer)
        SDL_DestroyRenderer(renderer);
    if (window)
        SDL_DestroyWindow(window);

    SDL_Quit();
}
