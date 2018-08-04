/******************************************************************************\
 *                                 log.c                                      *
 *                                 -----                                      *
 *                                                                            *
 *  The functions here are used to log actions in a progran.                  *
 *                                                                            *
 *  vlog(char *fmt, ...)                                                      *
 *      Log the formatted error message to the logfile.  cf. printf().        *
 *                                                                            *
\******************************************************************************/

#include <stdarg.h>
#include <stdio.h>
#include <stdlib.h>
#include <time.h>


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
    double  now = (double) clock() / CLOCKS_PER_SEC;    // time for this message

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    fd = fopen(LogFile, "a");
    if (LogPrefix)
        fprintf(fd, "%11.6f|%s: %s\n", now, LogPrefix, buff);
    else
        fprintf(fd, "%11.6f|%s\n", now, buff);
    fclose(fd);
    va_end(ap);
}
