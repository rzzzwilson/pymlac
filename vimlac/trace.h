/*
 * Interface for the vimlac trace routines.
 */

#ifndef TRACE_H
#define TRACE_H


extern bool TraceFlag;

void trace_open(void);
void trace_close(void);
void trace_start_line(void);
void trace_end_line(void);
void trace_regs(void);
void trace_dregs(void);
void trace_cpu(char *fmt, ...);
void trace_dcpu(char *fmt, ...);

#endif
