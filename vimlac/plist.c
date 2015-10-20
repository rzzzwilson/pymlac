/******************************************************************************\
 *                               plist.c                                      *
 *                              =========                                     *
 *                                                                            *
 *  This file implements a 'plist'-like structure to store a list of          *
 *  name/value pairs.  In this incarnation the plist stores names and values  *
 *  as char strings.                                                          *
 *                                                                            *
 *      PLIST PlistCreate(void);                                              *
 *                                                                            *
 *      void PListInsert(PLIST plist, char *name, char *value);               *
 *                                                                            *
 *      void *PlistFind(PLIST plist, char *name);                             *
 *                                                                            *
 *      void PlistDestroy(PLIST plist);                                       *
 *                                                                            *
 *      void PlistDump(PLIST plist);                                          *
 *                                                                            *
\******************************************************************************/

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <string.h>
#include <stdarg.h>

#include "plist.h"


/******
 * Define the plist header structure and data types.
 ******/

typedef struct _PList
{
    char *name;
    char *value;
    struct _PList *next;
} PList;


/******************************************************************************
       Name : error()
Description : printf()-like error routine.
 Parameters : params like printf()
    Returns : Doesn't, calls exit().
   Comments : 
 ******************************************************************************/
static void
error(char *fmt, ...)
{
    va_list ap;

    va_start(ap, fmt);
    vfprintf(stderr, fmt, ap);
    fprintf(stderr, "\n");
    va_end(ap);

    exit(1);
}


/******************************************************************************
       Name : PlistCreate()
Description : Routine to create a plist.
 Parameters : 
    Returns : Address (void *) of plist header.
   Comments : 
 ******************************************************************************/
PLIST
PlistCreate(void)
{
    PList *plist = malloc(sizeof(PList *));

    if (plist == NULL)
        error("Out of memory.");

    plist = NULL;

    return (PLIST) plist;
}


/******************************************************************************
       Name : PlistInsert()
Description : Function to insert new record into the property list.
 Parameters : htable  - address (void *) of plist header
            : record  - address (void *) of record to insert
            : recszie - size of record (bytes)
    Returns : 
   Comments : This routine takes a copy of the user record.
            : New record placed in front of any existing equal record.
 ******************************************************************************/
void
PListInsert(PLIST plist, char *name, char *value)
{
    PList *newrec = malloc(sizeof(PList));
    char *newname = malloc(strlen(name)+1);
    char *newvalue = malloc(strlen(value)+1);
    PList *hdr = (PList *) plist;

    if (newrec == NULL || newname == NULL || newvalue == NULL)
        error("Out of memory");

    strcpy(newname, name);
    strcpy(newvalue, value);

    newrec->next = NULL;
    newrec->name = newname;
    newrec->value = newvalue;

//    plist = (PList *) plist;

    newrec->next = hdr;
    hdr->next = newrec;
}


/******************************************************************************
       Name : PlistLookup()
Description : Look for a record in a plist.
 Parameters : plist - plist to look in
            : name  - the name to look for
    Returns : Returns pointer to value string or NULL if not found.
   Comments : 
 ******************************************************************************/
char *
PlistFind(PLIST plist, char *name)
{
    PList *hdr = (PList *) plist;

    while (hdr)
    {
        if (strcmp(hdr->name, name) == 0)
            return hdr->value;
    }

    return NULL;
}


/******************************************************************************
       Name : PlistDestroy()
Description : Destroy a property list.
 Parameters : plist - plist to destroy
    Returns : 
   Comments : 
 ******************************************************************************/
void
PlistDestroy(PLIST plist)
{
    PList *hdr = (PList *) plist;

    while (hdr)
    {
        PList *next = hdr->next;
        free(hdr->name);
        free(hdr->value);
        free(hdr);
        hdr = next;
    }
}


/******************************************************************************
       Name : PlistDump()
Description : Dump the plist to a specified open output FILE.
 Parameters : plist - plist to dump
            : output - FILE pointer to write to (stdout if NULL)
    Returns : 
   Comments : 
 ******************************************************************************/
void
PlistDump(PLIST plist, FILE *output)
{
    PList *hdr = (PList *) plist;

    if (output == NULL)
        output = stdout;

    while (hdr)
    {
        fprintf(output, "%s: %s\n", hdr->name, hdr->value);
        hdr = hdr->next;
    }
}
