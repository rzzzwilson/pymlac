/*
 * Trace routines for vimlac.
 */

#include <stdarg.h>

#include "vimlac.h"
#include "cpu.h"
#include "dcpu.h"
#include "log.h"


bool TraceFlag = true;
static char *TraceFile = "trace.out";
static FILE *trace_fp = NULL;
static char CPU_trace[64];
static char DCPU_trace[64];
static char CPU_reg_trace[64];
static char DCPU_reg_trace[64];


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
 * Description : Prepare a new trace outut.
 *  Parameters : 
 *     Returns : 
 *    Comments : 
 ******************************************************************************/
void
trace_start_line(void)
{
    // set output buffer to empty
    CPU_trace[0] = 0;
    DCPU_trace[0] = 0;
    CPU_reg_trace[0] = 0;
    DCPU_reg_trace[0] = 0;
}


/******************************************************************************
 * Description : Write stored data to the trace file.
 *  Parameters : 
 *     Returns : 
 *    Comments : 
 ******************************************************************************/
void
trace_end_line(void)
{
    fprintf(trace_fp, "%06o:     %-20s%-20s   %-s %-s\n",
                      cpu_get_prev_PC(), CPU_trace, DCPU_trace,
                                         CPU_reg_trace, DCPU_reg_trace);
    fflush(trace_fp);
}


/******************************************************************************
Description : printf()-style trace routine to dump main CPU registers.
 Parameters : 
    Returns : 
   Comments :
 ******************************************************************************/
void
trace_regs(void)
{
    TraceFlag = true;       // DEBUG

    if (TraceFlag != false)
    {
        sprintf(CPU_reg_trace, "AC=%06.6o L=%1.1o", cpu_get_AC(), cpu_get_L());
        vlog(CPU_reg_trace);
    }
}


/******************************************************************************
Description : printf()-style trace routine to dump dislpay CPU registers.
 Parameters : 
    Returns : 
   Comments :
 ******************************************************************************/
void
trace_dregs(void)
{
    TraceFlag = true;       // DEBUG

    if (TraceFlag != false)
    {
        sprintf(DCPU_reg_trace, "DPC=%06o X=%04o, Y=%04o",
                                dcpu_get_PC(), dcpu_get_x(), dcpu_get_y());
        vlog(DCPU_reg_trace);
    }
}


/******************************************************************************
Description : printf()-style trace routine for the CPU.
 Parameters : like printf()
    Returns : 
   Comments :
 ******************************************************************************/
void
trace_cpu(char *fmt, ...)
{
    TraceFlag = true;       // DEBUG

    if (TraceFlag != false)
    {
        va_list ap;

        va_start(ap, fmt);
        vsprintf(CPU_trace, fmt, ap);
        va_end(ap);

        trace_regs();
    }
}

/******************************************************************************
Description : printf()-style trace routine for the display CPU.
 Parameters : like printf()
    Returns :
   Comments :
 ******************************************************************************/
void
trace_dcpu(char *fmt, ...)
{
    TraceFlag = true;       // DEBUG

    if (TraceFlag != false)
    {
        va_list ap;

        va_start(ap, fmt);
        vsprintf(DCPU_trace, fmt, ap);
        va_end(ap);

        trace_dregs();
    }
}

