/*
 * Trace routines for vimlac.
 */

#include <stdarg.h>

#include "vimlac.h"
#include "cpu.h"


bool TraceFlag = false;


/******************************************************************************
 * Description : printf()-style output routine to RAW screen.
 *  Parameters : like printf()
 *     Returns : 
 *    Comments : 
 ******************************************************************************/
void
Emit(char *fmt, ...)
{
    va_list ap;
    char    buff[512];
    char    *chptr;
            
    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    va_end(ap);
                
    for (chptr = buff; *chptr != '\0'; ++chptr)
        fprintf(stdout, "%c", *chptr);
                    
    fflush(stdout);
}


void
DumpRegs(char *buff)
{
    sprintf(buff, "AC=0%6.6o\tL=%1.1o", cpu_get_AC(), cpu_get_L());
}


/******************************************************************************
Description : printf()-style trace routine to dump registers.
 Parameters : 
    Returns : 
   Comments :
 ******************************************************************************/
void
traceRegs(void)
{
    static char outbuff[512];

    if (TraceFlag != false)
    {
        char emitbuff[512];

        DumpRegs(outbuff);
        sprintf(emitbuff, "\t;%s", outbuff);
        Emit(emitbuff);
    }
}


/******************************************************************************
Description : printf()-style trace routine.
 Parameters : like printf()
    Returns : 
   Comments :
 ******************************************************************************/
void
trace(char *fmt, ...)
{
    static char outbuff[512];

    if (TraceFlag != false)
    {
        va_list ap;

        va_start(ap, fmt);
        vsprintf(outbuff, fmt, ap);
        va_end(ap);
        Emit("0%6.6o\t%s", cpu_get_prev_PC(), outbuff);
	traceRegs();
        Emit("\n");
    }
}
