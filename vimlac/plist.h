/******************************************************************************\
 *                               plist.h                                      *
 *                              =========                                     *
 *                                                                            *
 *  This file advertises the plist system interface.                          *
 *                                                                            *
\******************************************************************************/

#ifndef PLIST_H
#define PLIST_H

#include <stdio.h>

/******
 * Typedefs for user.
 ******/

typedef void *PLIST;


/******
 * Function prototypes.
 ******/

PLIST PlistCreate(void);
void PListInsert(PLIST plist, char *name, char *value);
char *PlistFind(PLIST plist, char *name);
void PlistDestroy(PLIST plist);
void PlistDump(PLIST plist, FILE *output);


#endif
