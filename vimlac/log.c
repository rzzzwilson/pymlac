/*
 * Log routines for the imlac simulator.
 */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>


char *LogFile = "vimlac.log";
char *LogPrefix = "";


/******************************************************************************
Description : printf()-style log routine.
 Parameters : like printf()
    Returns : 
   Comments : 
 ******************************************************************************/
void
vlog(char *fmt, ...)
{
    va_list ap;
    char    buff[1024];
    FILE    *fd;

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    fd = fopen(LogFile, "a");
    fprintf(fd, "%s: %s\n", LogPrefix, buff);
    fclose(fd);
    va_end(ap);
}
