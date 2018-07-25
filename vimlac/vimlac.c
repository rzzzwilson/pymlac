/*
 * The Virtual Imlac machine - a simulator for an Imlac PDS-1.
 *
 * Usage: vimlac [ <option> ]*
 *
 * That is, the user may specify zero or more options interspersed in any manner
 * required. The options are:
 * 
 *     -b (ptr | tty | none)         sets the bootstrap ROM code:
 *                                       ptr   uses the papertape bootstrap ROM
 *                                       tty   uses the teletype bootstrap ROM
 *                                       none  uses no bootstrap ROM
 *     -c                            clears core including bootstrap ROM, if write enabled
 *     -cf <filename>                sets the name of the core file to read and write
 *                                   (default file is 'pymlac.core')
 *     -d <value>                    sets the console data switches to the <value>
 *     -h                            prints this help
 *     -ptp <file>                   loads a file on to the papertape punch device
 *     -ptr <file>                   loads a file on to the papertape reader device
 *     -r (<address> | pc)           executes from <address> or the current PC contents
 *     -s <setfile>                  sets memory adress values from <setfile>
 *     -t (<range>[:<range>] | off)  controls the execution trace:
 *                                       -t 0100,0200            trace from 0100 octal to 200 decimal
 *                                       -t 0100,0200:0210,0300  trace from 0100 to 0200 and 0210 to 0300
 *                                       -t off                  turns trace off
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#include "vimlac.h"
#include "bootstrap.h"
#include "memory.h"
#include "ptrptp.h"
#include "cpu.h"
#include "log.h"


char *
strtolower(char *s)
{
    for (int i = 0; s[i]; i++)
    {
        s[i] = tolower(s[i]);
    }

    return s;
}


// Convert a string to an integer value.
// 
// s  the string to convert
// 
// The string may indicate a decimal or octal value.

int
str2int(char *s)
{
    if (s[0] == '0')
    {
        return strtoll(s, NULL, 8);
    }
    else
    {
        return strtoll(s, NULL, 10);
    }
}


void
run(WORD pc)
{
    cpu_set_PC(pc);
    cpu_start();
    while (true)
    {
       int cycles = cpu_execute_one();
       if (cycles < 1)
	   break;
       ptr_tick(cycles);
    }
}


void
usage(char *msg)
{
    if (strlen(msg) > 0)
    {
        printf("**************************************************************\n");
        printf("%s\n", msg);
        printf("**************************************************************\n");
        printf("\n");
    }
    printf("Usage: vimlac [ <option> ]*\n\n");
    printf("That is, the user may specify zero or more options interspersed in any manner\n");
    printf("required. The options are:\n");
    printf("\n");
    printf("    -b (ptr | tty | none)         sets the bootstrap ROM code:\n");
    printf("                                      ptr   uses the papertape bootstrap ROM\n");
    printf("                                      tty   uses the teletype bootstrap ROM\n");
    printf("                                      none  uses no bootstrap ROM\n");
    printf("    -c                            clears core including bootstrap ROM, if write enabled\n");
    printf("    -cf <filename>                sets the name of the core file to read and write\n");
    printf("                                  (default file is 'pymlac.core')\n");
    printf("    -d <value>                    sets the console data switches to the <value>\n");
    printf("    -h                            prints this help\n");
    printf("    -ptp <file>                   loads a file on to the papertape punch device\n");
    printf("    -ptr <file>                   loads a file on to the papertape reader device\n");
    printf("    -r (<address> | pc)           executes from <address> or the current PC contents\n");
    printf("    -s <setfile>                  sets memory adress values from <setfile>\n");
    printf("    -t (<range>[:<range>] | off)  controls the execution trace:\n");
    printf("                                      -t 0100,0200            trace from 0100 octal to 200 decimal\n");
    printf("                                      -t 0100,0200:0210,0300  trace from 0100 to 0200 and 0210 to 0300\n");
    printf("                                      -t off                  turns trace off\n");

    exit(1);
}


int
main(int argc, char *argv[])
{
    int ndx = 1;    // index into argv[]
    char *opt;      // pointer to command arg

    while (ndx < argc)
    {
        // get option, point at next command arg
        opt = argv[ndx];
        ndx += 1;

        if (*opt != '-')
        {
            usage("Bad option");
        }

        if (STREQ(opt, "-b"))
        {
            char *dev;      // pointer to boot device name

            if (ndx >= argc)
            {
                usage("'-b' option needs a following device name");
            }

            dev = strtolower(argv[ndx]);
            ndx += 1;
            if (STREQ(dev, "ptr"))
            {
                mem_set_rom(PtrROMImage);
            }
            else if (STREQ(dev, "tty"))
            {
                mem_set_rom(TtyROMImage);
            }
            else if (STREQ(dev, "none"))
                ;
            else
            {
                usage("-b option must be followed by 'ptr', 'tty' or 'none'");
            }
        }
        else if (STREQ(opt, "-c"))
        {
            mem_clear(0);
        }
        else if (STREQ(opt, "-cf"))
        {
            char *filename;     // pointer to filename string to load into memory

            if (ndx >= argc)
            {
                usage("'-cf' option needs a following filename");
            }

            filename = argv[ndx];
            ndx += 1;
            mem_load_core(filename);
        }
        else if (STREQ(opt, "-d"))
        {
            WORD value;         // value to load into data switches

            if (ndx >= argc)
            {
                usage("'-d' option needs a following data switch value");
            }

            value = str2int(argv[ndx]);
            ndx += 1;
            cpu_set_DS(value);
        }
        else if (STREQ(opt, "-h"))
        {
            usage("");
        }
        else if (STREQ(opt, "-ptp"))
        {
            char *filename;             // pointer to filename string

            if (ndx >= argc)
            {
                usage("'-ptp' option needs a following PTP filename");
            }
            filename = argv[ndx];
            ndx += 1;
            ptp_mount(filename);
        }
        else if (STREQ(opt, "-ptr"))
        {
            char *filename;         // pointer to PTR filename

            if (ndx >= argc)
            {
                usage("'-ptr' option needs a following PTR filename");
            }
            filename = argv[ndx];
            ndx += 1;
            ptr_mount(filename);
        }
        else if (STREQ(opt, "-r"))
        {
            char *address;          // pointer to start "address" string

            if (ndx >= argc)
            {
                usage("'-r' option needs a following address or 'pc'");
            }
            address = strtolower(argv[ndx]);
            ndx += 1;
            if (!STREQ(address, "pc"))
            {
                cpu_set_PC(str2int(address));
                vlog("Running from address %s", address);
            }
            else
            {
                vlog("Running from current PC %06o", cpu_get_PC());
            }
//            Trace.set_TraceMap(trace_map);
//            start_running(imlac_cpu, imlac_dcpu, imlac_memory, imlac_ptrptp, imlac_ttyin);
        }


    }

//    mem_clear(0);
//    mem_set_rom(PtrROMImage);
//    ptr_mount("test_add.ptp");
//    run(040);
//    run(0100);
//    mem_save_core("vimlac.core");
}


