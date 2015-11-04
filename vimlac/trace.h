/*
 * Interface for the vimlac trace routines.
 */

#ifndef TRACE_H
#define TRACE_H

void trace(char *fmt, ...);
void trace_open(void);
void trace_close(void);
void trace_delim(char *fmt, ...);

#endif
