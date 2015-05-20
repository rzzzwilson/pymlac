/******************************************************************************\
 *                                  iasm.c                                    *
 *                                 --------                                   *
 *                                                                            *
 *  The Imlac Cross Assembler.                                                *
 *                                                                            *
 *  Usage: iasm <option> <filename>                                           *
 *                                                                            *
 *  where <option>   is zero or more of                                       *
 *                     -bptr     use a papertape boot loader                  *
 *                     -btty     use a teletype boot loader                   *
 *                     -l <file> write listing to file <file>                 *
 *        <filename> is the file to assemble.                                 *
 *                                                                            *
 *  The input filename has the form of 'file.asm' and                         *
 *  the output file will be 'file.ptp' or 'file.tty'.                         *
 *                                                                            *
\******************************************************************************/


#include <getopt.h>

#include "iasm.h"
#include "assemble.h"


/******
 * Local constants.
 ******/

#define PASS1_FAIL              1
#define PASS2_FAIL              2


/******
 * File globals.
 ******/

static char *ProgName = "iasm";


/******
 * Application globals.
 ******/

char *InFileName = NULL;
FILE *InFile = NULL;

char OutFileName[MAXFILENAME_LEN + 1];
FILE *OutFile;

char *ListFileName = NULL;
FILE *ListFile;


/******************************************************************************
Description : Clone a string.
 Parameters : str - address of the string to duplicate
    Returns : The address of the new copied string.
   Comments : Couldn't get strdup() to work!?
 ******************************************************************************/
char *
CopyStr(char *str)
{
    char *result = NULL;

    if (str != NULL)
    {
        result = malloc(strlen(str) + 1);
        if (result == NULL)
            Error("Out of memory in file %s, line %d", __FILE__, __LINE__);

        strcpy(result, str);
    }

    return result;
}


/******************************************************************************
Description : printf()-style debug routine.
 Parameters : like printf()
    Returns : 
   Comments : 
 ******************************************************************************/
void
Debug(char *fmt, ...)
{
    va_list ap;
    char    buff[1024];

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    fprintf(stdout, "%s\n", buff);
    va_end(ap);
}


/******************************************************************************
Description : printf()-style error routine.
 Parameters : like printf()
    Returns : Doesn't, calls exit().
   Comments : 
 ******************************************************************************/
void
Error(char *fmt, ...)
{
    va_list ap;
    char    buff[1024];

    va_start(ap, fmt);
    vsprintf(buff, fmt, ap);
    fprintf(stdout, "%s\n", buff);
    va_end(ap);

    exit(EXIT_FAILURE);
}


/******************************************************************************
 Description : 
  Parameters : 
     Returns : 
    Comments : 
 ******************************************************************************/
static void
usage(void)
{
    fprintf(stderr, "usage: %s <option> <filename>\n", ProgName);
    fprintf(stderr, "where <option>   is zero or more of;\n");
    fprintf(stderr, "                   -l <file> write listing to file <file>\n");
    fprintf(stderr, "      <filename> is the file to assemble.\n");
    fprintf(stderr, "The input filename has the form of 'file.asm' and\n");
    fprintf(stderr, "the assembler output file will be 'file.ptp'.\n");

    fflush(stderr);

    exit(EXIT_FAILURE);
}


/******************************************************************************
 Description : 
  Parameters : 
     Returns : 
    Comments : 
 ******************************************************************************/
int
main(int argc, char *argv[])
{
    char optch;
    char *outputext = "ptp";
    int  exitvalue = EXIT_SUCCESS;

/******
 * Set up globals.
 ******/

    if (argv[0] != NULL)
        ProgName = argv[0];

/******
 * Check parameters.
 ******/

    opterr = 0;

    while ((optch = getopt(argc, argv, "l:")) != -1)
    {
        switch (optch)
        {
            case 'l':
                ListFileName = optarg;
                break;
            default:
                usage();
        }
    }

    if (optind + 1 != argc)
        usage();

    InFileName = argv[optind];
    InFile = fopen(InFileName, "r");
    if (InFile == NULL)
        Error("Can't open '%s' for first pass read: %s", InFileName, strerror(errno));

    if (strlen(InFileName) > 3 &&
        STREQ(InFileName + strlen(InFileName) - 4, ".asm"))
    {
        char *newname = CopyStr(InFileName);
        char *chptr = newname + strlen(newname) - 4;

        *chptr = '\0';
        sprintf(OutFileName, "%s.%s", newname, outputext);

        free(newname);
    }
    else
        sprintf(OutFileName, "%s.%s", InFileName, outputext);

    OutFile = fopen(OutFileName, "w");
    if (OutFile == NULL)
        Error("Can't open '%s' for output: %s", OutFileName, strerror(errno));

    if (ListFileName != NULL)
    {
        ListFile = fopen(ListFileName, "w");
        if (ListFile == NULL)
            Error("Can't open '%s' for list output: %s", ListFileName, strerror(errno));
    }

/******
 * Assemble the input file.
 ******/

    if (Pass1())
    {
        fclose(InFile);
        InFile = fopen(InFileName, "r");
        if (InFile == NULL)
            Error("Can't open '%s' for second pass read: %s", InFileName, strerror(errno));

        if (!Pass2())
            exitvalue = PASS2_FAIL;
    }
    else
        exitvalue = PASS1_FAIL;

/******
 * Close the files.
 ******/

    if (InFile != NULL)
        fclose(InFile);
    if (OutFile != NULL)
        fclose(OutFile);

    exit(exitvalue);
}


