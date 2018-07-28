/*
 * The Virtual Imlac machine - a simulator for an Imlac PDS-1.
 *
 * Usage: vimlac [ <option> ]*
 *
 * That is, the user may specify zero or more options interspersed in any manner
 * required. The options are executed from left to right and can be any of:
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
 *     -ttyin <file>                 loads <file> on to the teletype reader device
 *     -ttyout <file>                loads <file> on to the teletype writer device
 *     -v <file>                     write contents of core to <file>
 *     -w (on | off)                 set ROM write-protect to "on" or "off"
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>

#include "vimlac.h"
#include "bootstrap.h"
#include "memory.h"
#include "ptrptp.h"
#include "cpu.h"
#include "dcpu.h"
#include "trace.h"
#include "log.h"


//*********************************************************
// Conevrt a string to all lower case.
//
//     s  the string to convert (in situ)
//
// Returns the original string pointer.
//*********************************************************
char *
strtolower(char *s)
{
    for (int i = 0; s[i]; i++)
    {
        s[i] = tolower(s[i]);
    }

    return s;
}


//*********************************************************
// Convert a string to an integer value.
// 
//     s  the string to convert
// 
// The string may indicate a decimal or octal value.
//*********************************************************

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


//*********************************************************
// Run the emulator until the main/display CPU have
// both stopped.
//*********************************************************

//    Trace.init('pymlac.trace', cpu, dcpu)
//
//    cpu.running = True
//    while cpu.running:
//        Trace.start()
//
//        log(f'cpu.PC={cpu.PC}')
//        cycles = cpu.execute_one_instruction()
//        log(f'start_running: cpu.execute_one_instruction returned {cycles}')
//        dcycles = dcpu.execute_one_instruction()
//        log(f'start_running: dcpu.execute_one_instruction returned {dcycles}')
//        ptrptp.ptr_tick(cycles)
//        ptrptp.ptp_tick(cycles)
//        ttyin.tick(cycles)
//
//        Trace.end_line()
//        Trace.flush()
//
//    Trace.close()

void
run(WORD pc)
{
    cpu_set_PC(pc);
    cpu_start();
    trace_open();

    //while (cpu_running() && dcpu_running())
    while (cpu_running())
    {
        vlog("run: loop, PC=%06o", cpu_get_PC());
        trace_start_line();

        int cycles = cpu_execute_one();
        int dcycles = dcpu_execute_one();

        ptr_tick(cycles+dcycles);
        ptp_tick(cycles+dcycles);
//        ttyin_tick(cycles);

        trace_end_line();
    }

    trace_close();
}


//*********************************************************
// Print some help for the befuddled user.
//     msg  a message to print
//*********************************************************

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
    printf("required. The options are executed from left to right and can be any of:\n");
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
    printf("    -ttyin <file>                 loads <file> on to the teletype reader device\n");
    printf("    -ttyout <file>                loads <file> on to the teletype writer device\n");
    printf("    -v <file>                     write contents of core to <file>\n");
    printf("    -w (on | off)                 set ROM write-protect to 'on' or 'off'\n");
    exit(1);
}


//*********************************************************
// Start the emulator.
//*********************************************************

int
main(int argc, char *argv[])
{
    int ndx = 1;    // index into argv[]
    char *opt;      // pointer to command arg

    vlog("vimlac %s", VIMLAC_VERSION);

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
            WORD run_pc;
            if (!STREQ(address, "pc"))
            {
                cpu_set_PC(str2int(address));
                vlog("Running from address %s", address);
                run_pc = str2int(address);
            }
            else
            {
                vlog("Running from current PC %06o", cpu_get_PC());
                run_pc = cpu_get_PC();
            }
//            Trace.set_TraceMap(trace_map);
//            start_running(imlac_cpu, imlac_dcpu, imlac_memory, imlac_ptrptp, imlac_ttyin);
            run(run_pc);
        }
        else if (STREQ(opt, "-s"))
        {
            char *filename;         // pointer to filename to load memory from

            if (ndx >= argc)
            {
                usage("'-s' option needs a following data filename");
            }

            filename = argv[ndx];
            ndx += 1;
            mem_load_core(filename);
        }
#ifdef JUNK
        else if (STREQ(opt, "-t"))
        {
            char *t;                // pointer to trace limits string

            if (ndx >= argc)
            {
                usage("'-t' option needs following address ranges or 'off'");
            }
            r = argv[ndx];
            ndx += 1;
//            trace_map = collections.defaultdict(bool)
            if (!STREQ(r, "off"))
            {
                for rng in r.split(":"):
                    be = rng.split(",")
                    if len(be) != 2:
                        usage("'-t' ranges must have form 'begin,end'")
                        sys.exit(10)
                    (begin, end) = be
                    begin = str2int(begin)
                    end = str2int(end)
                    for addr in range(begin, end+1):
                        trace_map[addr] = True
            }
            else
            {
            }
        }
#endif
        else if (STREQ(opt, "-ttyin"))
        {
            char *filename;         // pointer to filename to mount on TTYIN

            if (ndx >= argc)
            {
                usage("'-ttyin' option needs a following data filename");
            }
            filename = argv[ndx];
            ndx += 1;
//            imlac_ttyin.mount(filename)
        }
        else if (STREQ(opt, "-ttyout"))
        {
            char *filename;         // pointer to filename to mount on TTYOUT

            if (ndx >= argc)
            {
                usage("'-ttyout' option needs a following data filename");
            }

            filename = argv[ndx];
            ndx += 1;
//            imlac_ttyout.mount(filename)
        }
        else if (STREQ(opt, "-v"))
        {
            char *filename;         // pointer to filename to write mem info to

            if (ndx >= argc)
            {
                usage("'-v' option needs a following address filename");
            }

            filename = argv[ndx];
            ndx += 1;
//            view_mem(filename)
        }
        else if (STREQ(opt, "-w"))
        {
            char *state_str;        // pointer to ROM state string
            bool state = true;      // ROM write-protect state

            if (ndx >= argc)
            {
                usage("'-v' option needs a following 'on' or 'off'");
            }

            state_str = argv[ndx];
            ndx += 1;
            if (STREQ(state_str, "on"))
            {
                state = true;
            }
            else if (STREQ(state_str, "off"))
            {
                state = false;
            }
            else
            {
                usage("'-v' option needs a following 'on' or 'off'");
            }
            mem_set_rom_readonly(state);
        }
        else
        {
            char buff[1024];

            sprintf(buff, "Unrecognized option '%s'", opt);
            usage(buff);
        }
    }
}
