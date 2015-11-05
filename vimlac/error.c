/*
 * Error routines for the imlac simulator.
 */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>


/******************************************************************************
Description : printf()-style trace routine.
 Parameters : like printf()
    Returns : 
   Comments : 
 ******************************************************************************/
void
error(char *fmt, ...)
{
    va_list ap;
    char    buff[1024];

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    fprintf(stderr, "\n%s\n", buff);
    va_end(ap);

    exit(10);
}
