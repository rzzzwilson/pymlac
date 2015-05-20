/******************************************************************************\
 *                                  iasm.h                                    *
 *                                 --------                                   *
 *                                                                            *
 *  All global definitions for the Imlac Cross Assembler.                     *
 *                                                                            *
\******************************************************************************/


#ifndef IASM_H
#define IASM_H

#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <ctype.h>
#include <errno.h>


/******
 * Global macros, constants.
 ******/

#define MAXFILENAME_LEN         1024

#define STREQ(a,b)		(strcmp((a),(b))==0)
#define STRIEQ(a,b)		(strcasecmp((a),(b))==0)

#ifndef BOOL
    typedef enum
    {
        FALSE = 0,
        TRUE
    } BOOL;
#endif


/******
 * Global variables.
 ******/

char *InFileName;
FILE *InFile;

char OutFileName[MAXFILENAME_LEN + 1];
FILE *OutFile;

char *ListFileName;
FILE *ListFile;

BOOL PTRBoot;


/******
 * Global functions.
 ******/

char *CopyStr(char *str);
void Debug(char *fmt, ...);
void Error(char *fmt, ...);


#endif
