/*
 * Log routines for the imlac simulator.
 */

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>


char *LogFile = "vimlac.log";
char *LogPrefix = NULL;


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
    if (LogPrefix)
        fprintf(fd, "%s: %s\n", LogPrefix, buff);
    else
        fprintf(fd, "%s\n", buff);
    fclose(fd);
    va_end(ap);
}
