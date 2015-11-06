/*
 * Trace routines for vimlac.
 */

#include <stdarg.h>

#include "vimlac.h"
#include "cpu.h"


bool TraceFlag = false;
static char *TraceFile = "trace.out";
static FILE *trace_fp = NULL;


/******************************************************************************
 * Description : printf()-style output routine to RAW screen.
 *  Parameters : like printf()
 *     Returns : 
 *    Comments : 
 ******************************************************************************/
void
trace_open(void)
{
    trace_fp = fopen(TraceFile, "a");
    TraceFlag = true;
}


/******************************************************************************
 * Description : printf()-style output routine to RAW screen.
 *  Parameters : like printf()
 *     Returns : 
 *    Comments : 
 ******************************************************************************/
void
trace_close(void)
{
    if (trace_fp != NULL)
        fclose(trace_fp);
    trace_fp = NULL;
    TraceFlag = false;
}


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
        fprintf(trace_fp, "%c", *chptr);
                    
    fflush(trace_fp);
}


void
DumpRegs(char *buff)
{
    sprintf(buff, "AC=0%6.6o\tL=%1.1o", cpu_get_AC(), cpu_get_L());
}

void
trace_delim(char *fmt, ...)
{
    va_list ap;
    char    buff[1024];

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    va_end(ap);

    Emit("%s\n", buff);
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
