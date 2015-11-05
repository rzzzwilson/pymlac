/*
 * Test the CPU implementation.
 *
 * We implement a small interpreter to test the CPU.  The DSL implemented is
 * documented at: https://github.com/rzzzwilson/pymlac/wiki/pymlac%20DSL
 *
 * If a test line finds no error, print nothing.
 * If any errors are found, print line followed by all errors.
 */

#include <stdio.h>
#include <stdlib.h>
#include <ctype.h>
#include <getopt.h>

#include "vimlac.h"
#include "cpu.h"
#include "dcpu.h"
#include "memory.h"
#include "ptrptp.h"
#include "error.h"
#include "log.h"
#include "plist.h"
#include "bootstrap.h"
#include "trace.h"


// constants
const char *LstFilename = "_#TEST#_.lst";   // LST filename
const char *AsmFilename = "_#TEST#_.asm";   // ASM filename

const int InitMemValue = 0;
const int InitRegValue = 0;

const int MaxLineSize = 4096;               // max length of one script line

// command structures
typedef struct _Command
{
    struct _Command *next;
    char *opcode;
    char *field1;
    char *field2;
    char *orig2;
} Command;

typedef struct _Test
{
    struct _Test *next;
    int line_number;
    Command *commands;
} Test;

typedef struct _Assoc
{
    struct _Assoc *next;
} Assoc;


typedef struct _Opcode
{
    WORD opcode;
    struct _Opcode *next;
} Opcode;


bool DisplayOn = false;
int UsedCycles = 0;
WORD RegAllValue = 0;
WORD MemAllValue = 0;
PLIST MemValues = NULL;
PLIST RegValues = NULL;

// progress indicator strings
char *Progress[] = { "\r/",
                     "\r|",
                     "\r\\",
                     "\r-" };
#define NUMELTS(a)  (sizeof((a))/sizeof((a)[0]))


/******************************************************************************
Description : Show progress while we process tests.
 Parameters : lnum - line number
    Returns :
   Comments : 
 ******************************************************************************/
void
show_progress(int lnum)
{
    printf("\b\b\b\b\b\b\b\bTest %03d\r", lnum);
    fflush(stdout);
}


/******************************************************************************
Description : Convert a string to upper case.
 Parameters : str - address of string to convert
    Returns :
   Comments : The string is converted 'in situ'.
 ******************************************************************************/
void
strupper(char *str)
{
    while (*str)
    {
        *str = toupper(*str);
        ++str;
    }
}


/******************************************************************************
Description : Convert a string to lower case.
 Parameters : str - address of string to convert
    Returns :
   Comments : The string is converted 'in situ'.
 ******************************************************************************/
void
strlower(char *str)
{
    while (*str)
    {
        *str = tolower(*str);
        ++str;
    }
}


/******************************************************************************
Description : Convert a string value into a WORD integer.
 Parameters : str - address of string holding [0-9] characters
    Returns : A WORD value containing the integer number in 'str'.
   Comments : 'str' may contain a decimal or octal string representation.
 ******************************************************************************/
WORD
str2word(char *str)
{
    WORD value = 0;

    if (*str == '0')
    {   // octal
        sscanf(str, "%o", &value);
    }
    else
    {   // decimal
        sscanf(str, "%d", &value);
    }

    return value;
}


/******************************************************************************
Description : Create a new string which is a copy of the given string.
 Parameters : str - the string to copy
    Returns : The address of the new (maoolc) string.
   Comments : The caller must ensure this new string is free'd.
 ******************************************************************************/
char *
new_String(char *str)
{
    char *result = (char *) malloc(strlen(str)+1);
    strcpy(result, str);
    strupper(result);
    return result;
}

/******************************************************************************
Description : Print contents of a Command to stdout.
 Parameters : cmd - address of the Command to dump
    Returns :
   Comments :
 ******************************************************************************/
void
dump_cmd(Command *cmd)
{
    printf("\n~ Command ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
    printf("address: %p   next: %p\n", cmd, cmd->next);
    printf("opcode:  %s   field1: %s   field2: %s\n",
            cmd->opcode, cmd->field1, cmd->field2);
    printf("original: %s\n", cmd->orig2);
    printf("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n");
}

/******************************************************************************
Description : Split a string into head/tail using delimiter char.
 Parameters : str    string to split
            : delim  character to split string on
    Returns : Pointer to tail string, NULL if no tail.
   Comments : The input string is destroyed in-situ.
            : Usage something like:
            :     char *str = "abc|rst|xyz";
            :     char *new_str;
            :     while (new_str = split(str, '|')
            :     {
            :         process(str);     // do something with head
            :         str = new_str;    // move to tail, repeat
            :     }
 ******************************************************************************/
char *
split(char *str, char delim)
{
    char *result = strchr(str, delim);

    if (result != NULL)
    {
        *result = '\0';
        ++result;
    }

    return result;
}


////////////////////////////////////////////////////////////////////////////////
// The following routines wrap the 'plist' functions so we are handling data
// formats useful to the test code.  We want to handle WORD values and WORD
// memory addresses but the 'plist' routines only handle strings.  The code here
// converts to/from strings.
////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
Description : Save a register value to the RegValues plist.
 Parameters : name - string holding register name
            : val  - binary value to save
    Returns :
   Comments : The value is converted to a fixed string form.
 ******************************************************************************/
void
save_reg_plist(char *name, WORD val)
{
    char *new_name = new_String(name);
    char *new_value = malloc(8);

    sprintf(new_value, "%07o", val);

    PlistInsert(RegValues, new_name, new_value);
}


/******************************************************************************
Description : Get a register value from the RegValues plist.
 Parameters : name   - string holding register name
            : result - address of WORD to hold result
    Returns : true if register in PLIST and value is at *result.
   Comments :
 ******************************************************************************/
bool
get_reg_plist(char *name, WORD *result)
{
    char *new_name = new_String(name);
    char *value = PlistFind(RegValues, new_name);

    if (value)
    {
        *result = str2word(value);
        return true;
    }

    return false;
}


/******************************************************************************
Description : Save a memory value to the RegValues plist.
 Parameters : addr - the binary memory address
            : val  - binary value to save
    Returns :
   Comments : The address & value are converted to a fixed string form.
 ******************************************************************************/
void
save_mem_plist(WORD addr, WORD val)
{
    char *new_addr = malloc(8);
    char *new_value = malloc(8);

    sprintf(new_addr, "%07o", addr);
    sprintf(new_value, "%07o", val);

    PlistInsert(MemValues, new_addr, new_value);
}


/******************************************************************************
Description : Save a memory value to the RegValues plist.
 Parameters : addr  - the binary memory address
            : value - address of WORD to save value in
    Returns : 'true' if found, and *level contains result.
   Comments : The address is converted to a fixed string form.
 ******************************************************************************/
bool
get_mem_plist(WORD addr, WORD *value)
{
    char *new_addr = malloc(8);
    sprintf(new_addr, "%07o", addr);

    char *result = PlistFind(MemValues, new_addr);

    if (result)
    {
        *value = str2word(result);
        return true;
    }

    return false;
}

////////////////////////////////////////////////////////////////////////////////
// Here we implement the DSL primitives.  They all take two parameters which are
// the DSL field1 and field2 values (lowercase strings).  If one or both are
// missing the parameter is None.
//
//   setreg <name> <value>
//   setmem <address> <value>
//   allreg <value>
//   allmem <value>
//   bootrom <type>
//   romwrite <bool>
//   run [<number>]
//   rununtil <address>
//   checkcycles <number>
//   checkreg <name> <value>
//   checkmem <addr> <value>
//   checkcpu <state>
//   checkdcpu <state>
//   mount <device> <filename>
//   dismount <device>
//   checkfile <file1> <file2>
////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
Description : Set a register to a value
 Parameters : name - string containing register name (uppercase)
            : fld2 - string containing field 2
    Returns : The number of errors encountered (0 or 1).
   Comments : Sets globals used to check after execution.
 ******************************************************************************/
int
setreg(char *name, char *fld2)
{
    int result = 0;
    WORD value = str2word(fld2);

    if (STREQ(name, "AC"))
        cpu_set_AC(value);
    else if (STREQ(name, "L"))
        cpu_set_L(value);
    else if (STREQ(name, "PC"))
        cpu_set_PC(value);
    else if (STREQ(name, "DS"))
        cpu_set_DS(value);
    else
    {
        vlog("setreg: bad register name: %s", name);
        return 1;
    }

    save_reg_plist(name, value);

    return result;
}


/******************************************************************************
Description : Set a memory cell to a value;
 Parameters : addr - address of memory cell (string)
            : fld2 - string conatining one or more values to put into memory
            :        (eg, "123|234|345" or "12345")
    Returns : The number of errors encountered (0 or 1).
   Comments : Sets globals used to check after execution.
 ******************************************************************************/
int
setmem(char *addr, char *fld2)
{
    WORD address = str2word(addr);
    char *new_fld2;
    WORD value = 0;

    while ((new_fld2 = split(fld2, '|')))
    {
        value = str2word(fld2);

        trace_delim("setmem: setting address %07o to value %07o", address, value);

        mem_put(address, false, value);
        save_mem_plist(address, value);
        ++address;
        fld2 = new_fld2;
    }

    // handle last part of field
    value = str2word(fld2);
    trace_delim("setmem: setting address %07o to value %07o", address, value);
    mem_put(address, false, value);
    save_mem_plist(address, value);

    return 0;
}


/******************************************************************************
Description : Set all registers to a value.
 Parameters : value - value to put into registers (string)
            : var2  - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
allreg(char *value, char *var2)
{
    int val = str2word(value);

    RegAllValue = val;

    cpu_set_AC(val);
    save_reg_plist("AC", val);
    cpu_set_L(val & 1);
    save_reg_plist("L", val & 1);
    cpu_set_PC(val);
    save_reg_plist("PC", val);
    cpu_set_DS(val);
    save_reg_plist("DS", val);

    return 0;
}


/******************************************************************************
Description : Set all memory locations to a value.
 Parameters : value - value to put into memory (string)
            : var2  - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
allmem(char *value, char *var2)
{
    int val = str2word(value);

    MemAllValue = val;

    for (WORD adr = 0; adr < MEM_SIZE; ++adr)
        mem_put(adr, false, val);

    return 0;
}


/******************************************************************************
Description : Set the boot ROM to a papertape or TTY bootstrap.
 Parameters : type   - type of ROM, eother 'PTR', 'TTY' or NULL
            : ignore - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
bootrom(char *type, char *ignore)
{
    if (STREQ(type, "PTR"))
        mem_set_rom(PtrROMImage);
    else if (STREQ(type, "TTY"))
        mem_set_rom(TtyROMImage);
    else
    {
        vlog("boot_rom: bad bootstrap type: %s", type);
        return 1;
    }
    return 0;
}


/******************************************************************************
Description : Set the ROM write capability.
 Parameters : write  - sets if ROM writable, "ON" or "OFF"
            : ignore - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
romwrite(char *write, char *fld2)
{
    if (STREQ(write, "ON"))
        mem_set_rom_readonly(false);
    else if (STREQ(write, "OFF"))
        mem_set_rom_readonly(true);
    else
    {
        vlog("romwrite: bad ROM writable code: %s", write);
        return 1;
    }
    return 0;
}


/******************************************************************************
Description : Run one or more instructions on the CPU.
 Parameters : num    - the number of instructions to run (assume 1 if NULL)
            : ignore - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
run(char *num, char *ignore)
{
    int run_num = 0;

    // if not given a number of instructions, assume 1
    if (!num)
        num = "1";

    run_num = str2word(num);

    cpu_start();
    while (run_num--)
    {
        int cycles = cpu_execute_one();

        ptr_tick(cycles);
        ptp_tick(cycles);

        UsedCycles += cycles;
    }

    return 0;
}


/******************************************************************************
Description : Run the CPU until PC is the same as 'addr'.
 Parameters : addr   - PC contents to stop at
            : ignore - unused
    Returns : The number of errors encountered (0 or 1).
   Comments : We execute one instruction before checking PC.
 ******************************************************************************/
int
rununtil(char *addr, char *ignore)
{
    WORD stop_pc = str2word(addr);

    cpu_start();
    while (cpu_running())
    {
        int cycles = cpu_execute_one();

        ptr_tick(cycles);
        ptp_tick(cycles);

        UsedCycles += cycles;
        if (cpu_get_PC() == stop_pc)
            break;
    }

    return 0;
}


/******************************************************************************
Description : Check that the number of cycles used is as expected.
 Parameters : cycles  - number of cycles expected
            : ignore  - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkcycles(char *cycles, char *ignore)
{
    WORD c = str2word(cycles);

    if (c != UsedCycles)
    {
        vlog("Test used %d cycles, expected %d!?", UsedCycles, c);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Check that a register contents is as expected.
 Parameters : reg      - string holding register name
            : expected - expected register value (string)
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkreg(char *reg, char *expected)
{
    WORD exp = str2word(expected);
    WORD value;

    if (STREQ(reg, "AC")) value = cpu_get_AC();
    else if (STREQ(reg, "L")) value = cpu_get_L();
    else if (STREQ(reg, "PC")) value = cpu_get_PC();
    else if (STREQ(reg, "DS")) value = cpu_get_DS();
    else
    {
        vlog("checkreg: bad register name: %s", reg);
        return 1;
    }

    // check register contents
    save_reg_plist(reg, value);
    if (value != exp)
    {
        vlog("register %s is %07o, should be %07o", reg, value, exp);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Check that the main CPU is in the correct state.
 Parameters : state  - string holding expected display state ('on' or 'off)
            : unused - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkcpu(char *state, char *unused)
{
    if ((STREQ(state, "on")) && !cpu_running())
    {
        vlog("Main CPU run state is %s, should be 'ON'",
                (DisplayOn ? "ON": "OFF"));
        return 1;
    }
    else if ((STREQ(state, "off")) && cpu_running())
    {
        vlog("Main CPU run state is %s, should be 'OFF'",
                (DisplayOn ? "ON": "OFF"));
        return 1;
    }
    else
    {
        vlog("checkcpu: state should be 'on' or 'OFF', got %s", state);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Check that the display is in the correct state.
 Parameters : state  - string holding expected display state ('on' or 'off)
            : unused - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkdcpu(char *state, char *unused)
{
    if ((STREQ(state, "on")) && !DisplayOn)
    {
        vlog("Display CPU run state is %s, should be 'ON'",
                (DisplayOn ? "ON": "OFF"));
        return 1;
    }
    else if ((STREQ(state, "off")) && DisplayOn)
    {
        vlog("Display CPU run state is %s, should be 'OFF'",
                (DisplayOn ? "ON": "OFF"));
        return 1;
    }
    else
    {
        vlog("checkd: state should be 'on' or 'OFF', got %s", state);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Mount a file on a device.
 Parameters : device   - a device name ("PTR", "PTP", "TTYIN" or "TTYOUT")
            : filename - path to the file to mount
    Returns : The number of errors encountered (0 or 1).
   Comments : If the device is an input device the file *must* exist.
 ******************************************************************************/
int
mount(char *device, char *filename)
{
    strlower(filename);

    if (STREQ(device, "PTR"))
        ptr_mount(filename);
    else if (STREQ(device, "PTP"))
        ptp_mount(filename);
    else
    {
        vlog("mount: mount device name not recognized: %s", device);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Dismount a file on a device.
 Parameters : device  - a device name ("PTR", "PTP", "TTYIN" or "TTYOUT")
            : ignore  - unused
    Returns : The number of errors encountered (0 or 1).
   Comments : 
 ******************************************************************************/
int
dismount(char *device, char *ignore)
{
//    strupper(device);

    if (STREQ(device, "PTR"))
        ptr_dismount();
    else if (STREQ(device, "PTP"))
        ptp_dismount();
    else
    {
        vlog("dismount: device name not recognized: %s", device);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Checkk that two files are identical.
 Parameters : file1, file2 - files to check
    Returns : The number of errors encountered (0 or 1).
   Comments : 
 ******************************************************************************/
int
checkfile(char *file1, char *file2)
{
    char buffer[1024];

    strlower(file1);
    strlower(file2);

    // assemble the file
    sprintf(buffer, "cmp %s %s >/dev/null 2>&1", file1, file2);
    printf("%s\n", buffer);
    if (system(buffer) == -1)
    {
        vlog("checkfile: files '%s' and '%s' differ", file1, file2);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Check that a memory address contents is as expected.
 Parameters : address - memory address to check (string)
            : value   - expected memory value (string)
    Returns : The number of errors encountered (0 or 1).
   Comments : We check the MemValues plist first!
 ******************************************************************************/
int
checkmem(char *address, char *value)
{
    WORD adr = str2word(address);
    WORD val = str2word(value);
    WORD memvalue;

    // check actual memory
    memvalue = mem_get(adr, false);
    save_mem_plist(adr, memvalue);
    if (memvalue != val)
    {
        vlog("Memory at address %07o is %07o, should be %07o",
                adr, memvalue, val);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Check that the CPU run state is as expected.
 Parameters : state  - the expected CPU state (string, 'ON' or 'OFF')
            : unused - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkrun(char *state, char *unused)
{
    bool cpu_state = cpu_running();

    if (!STREQ(state, "ON") && !STREQ(state, "OFF"))
    {
        vlog("checkrun: state should be 'ON' or 'OFF', got '%s'", state);
        return 1;
    }

    if (STREQ(state, "ON") && !cpu_state)
    {
        vlog("CPU run state is 'OFF', should be 'ON'");
        return 1;
    }

    if (STREQ(state, "OFF") && cpu_state)
    {
        vlog("CPU run state is 'ON', should be 'OFF'");
        return 1;
    }

    return 0;
}


////////////////////////////////////////////////////////////////////////////////

/******************************************************************************
Description : Constructor for a Command struct.
 Parameters : opcode - the opcode value for the struct
    Returns : The address of a new Command struct.
   Comments : The ->next, ->field1 and ->field2 fields are NULL.
 ******************************************************************************/
Command *
new_Command(char *opcode)
{
    Command *result = (Command *) malloc(sizeof(Command));

    result->opcode = (char *) malloc(strlen(opcode)+1);
    strcpy(result->opcode, opcode);
    strupper(result->opcode);

    result->next = NULL;
    result->field1 = NULL;
    result->field2 = NULL;
    result->orig2 = NULL;

    return result;
}


/******************************************************************************
Description : Constructor for a Test struct.
 Parameters : line_number - the number of the line that created the Test
            : commands    - address of chain of commands for Test
    Returns : The address of a new Test struct.
   Comments : The ->next field is NULL.
 ******************************************************************************/
Test *
new_Test(int line_number, Command *commands)
{
    Test *result = (Test *) malloc(sizeof(Test));

    result->next = NULL;
    result->line_number = line_number;
    result->commands = commands;

    return result;
}


/******************************************************************************
Description : Function to provide help to the befuddled user.
 Parameters : msg - if not NULL, a message to display
    Returns :
   Comments :
 ******************************************************************************/
void
usage(char *msg)
{
    char *delim = "******************************"
                  "******************************";

    if (msg != NULL)
    {
        fprintf(stderr, "%s\n", delim);
        fprintf(stderr, "%s\n", msg);
        fprintf(stderr, "%s\n\n", delim);
    }

    fprintf(stderr, "Test pymlac CPU opcodes DIRECTLY.\n\n");

    fprintf(stderr, "Usage: test_CPU.py [<options>] <filename>\n\n");

    fprintf(stderr, "where <filename> is a file of test instructions and\n");
    fprintf(stderr, "      <options> is one or more of\n");
    fprintf(stderr, "          -h    prints this help and stops\n");
}


/******************************************************************************
Description : Function to return the imlac binary opcode of an instruction.
 Parameters : addr   - address of the instruction
            : opcode - string containing the instruction
    Returns : A linked list of binary opcodes.
   Comments : We already have an assembler, so we just reuse it.  Generate an
            : ASM file, assemble it and pick out the opcodes from the LST file.
 ******************************************************************************/
Opcode *
assemble(WORD addr, char *opcodes)
{
    FILE *fd;
    char buffer[128];
    Opcode *result = NULL;
    Opcode *last_result = NULL;
    char *strcopy = new_String(opcodes);
    char *old_strcopy = strcopy;
    char *new_strcopy;
    int  num_opcodes = 0;

    // create the ASM file
    fd = fopen(AsmFilename, "wb");
    fprintf(fd, "\torg\t%07o\n", addr);
    while ((new_strcopy = split(strcopy, '|')))
    {
        fprintf(fd, "\t%s\n", strcopy);
        ++num_opcodes;
        strcopy = new_strcopy;
    }
    // handle last opcode
    fprintf(fd, "\t%s\n", strcopy);
    ++num_opcodes;

    fprintf(fd, "\tend\n");
    fclose(fd);
    free(old_strcopy);

    // assemble the file
    sprintf(buffer, "../iasm/iasm -l %s %s", LstFilename, AsmFilename);
    if (system(buffer) == -1)
        error("Error doing: %s", buffer);

    // read LST file for opcodes on second and subsequent
    fd = fopen(LstFilename, "rb");

    // skip first line - ORG
    if (fgets(buffer, sizeof(buffer), fd) == NULL)
        error("Error reading %s", LstFilename);

    while (num_opcodes-- > 0)
    {
        Opcode *new_opcode = malloc(sizeof(Opcode));

        new_opcode->next = NULL;

        // get next line of assembler listing
        if (fgets(buffer, sizeof(buffer), fd) == NULL)
            error("Error reading %s", LstFilename);

        // read first word value
        if (sscanf(buffer, "%o", &new_opcode->opcode) != 1)
            error("Badly formatted assembler output: %s", buffer);

        // add binary opcode to end of result list
        if (result == NULL)
        {
            result = last_result = new_opcode;
        }
        else
        {
            last_result->next = new_opcode;
            last_result = new_opcode;
        }
    }

    fclose(fd);

    return result;
}


/******************************************************************************
Description : Decide if buffer line should be skipped.
 Parameters : buffer - address of line buffer
    Returns : 'true' if line should be skipped (no commands)
   Comments : Skip if line empty or column 1 is '#'.
 ******************************************************************************/
bool
should_skip(char *buffer)
{
    char *scan = buffer;

    if (buffer[0] == '#')
        return true;

    while (*scan)
    {
        if (!isspace(*scan))
            return false;
        ++scan;
    }

    return true;
}


/******************************************************************************
Description : Parse one command string and populate a new Command struct.
 Parameters : scan - address of command string
    Returns : Address of the new Command struct.
   Comments : result->next is set to NULL.
            : A command is one, two or three fields.
 ******************************************************************************/
Command *
parse_one_cmd(char *scan)
{
    Command *result = NULL;
    char *opcode;
    char *field1 = NULL;
    char *field2 = NULL;
    char *orig2 = NULL;
    char tmpbuff[256];

    // find start and end of opcode
    while (*scan && isspace(*scan))     // skip leading space
        ++scan;
    opcode = scan;
    strupper(opcode);
    while (*scan && !isspace(*scan))
        ++scan;
    if (*scan)
        *(scan++) = '\0';

    // start/end of field1 (if there)
    while (*scan && isspace(*scan))     // skip leading space
        ++scan;

    if (*scan)
    {   // we have field1, at least
        field1 = scan;
        while (*scan && !isspace(*scan))
            ++scan;
        if (*scan)
            *(scan++) = '\0';

        // field2?
        while (*scan && isspace(*scan)) // skip leading space
            ++scan;

        if (*scan)
        {
            // we do have field2
            field2 = scan;
            if (*field2 == '[')
            {   // assembler field
                orig2 = new_String(field2);
                ++field2;
                while (*scan && !(*scan == ']'))
                    ++scan;
                *scan = '\0';
                Opcode *v = assemble(str2word(field1), field2); // destroys field2
                while (v)
                {
                    sprintf(tmpbuff+strlen(tmpbuff), "|%d", v->opcode);
                    v = v->next;
                }
                field2 = tmpbuff+1;
            }
            else
            {
                while (*scan && !isspace(*scan))
                    ++scan;
                *scan = '\0';
            }
        }
    }

    // create new Command struct
    result = new_Command(opcode);

    if (field1)
        result->field1 = new_String(field1);
    else
        result->field1 = NULL;

    if (field2)
        result->field2 = new_String(field2);
    else
        result->field2 = NULL;

    result->orig2 = orig2;

    return result;
}


/******************************************************************************
Description : Read the command buffer and create a chain of Command structs.
 Parameters : scriptpath - script filename
    Returns : Pointer to a chain of Command structs.
   Comments :
 ******************************************************************************/
Command *
parse_cmds(char *scan)
{
    Command *result = NULL;
    Command *last_result = NULL;
    char *end_cmd = NULL;
    Command *new_cmd = NULL;

    // scan the buffer for commands
    do
    {
        char *new_scan = NULL;

        while (*scan && isspace(*scan))
            ++scan;

        end_cmd = strchr(scan, ';');
        if (end_cmd)
        {
            new_scan = end_cmd + 1;
            *end_cmd = '\0';
        }

        new_cmd = parse_one_cmd(scan);

        if (result == NULL)
        {
            result = new_cmd;
            last_result = result;
        }
        else
        {
            last_result->next = new_cmd;
            last_result = new_cmd;
        }

        scan = new_scan;
    } while (scan && *scan);

    return result;
}


/******************************************************************************
Description : Read the script file and create a chain of Test structs.
 Parameters : scriptpath - script filename
    Returns : Pointer to a chain of Test structs.
   Comments :
 ******************************************************************************/
Test *
parse_script(char *scriptpath)
{
    Test *head_test = NULL;         // head of Test chain
    Test *last_test = NULL;         // pointer to last Test found
    Command *last_cmd = NULL;       // pointer to last Command found
    char buffer[MaxLineSize];       // buffer to read each line into
    char *scan;                     // buffer scan pointer
    FILE *fd;
    int line_number = 0;

    // open script file
    fd = fopen(scriptpath, "rb");

    // read script file, handle each line
    while (true)
    {
        // bump line numebr to that next read in
        ++line_number;

        // some indication of progress
        show_progress(line_number);

        // NULL fill buffer so we can tell if line too long
        memset(buffer, (char) NULL, sizeof(buffer));

        // get next line, break out of loop on end of file
        if (fgets(buffer, sizeof(buffer), fd) == NULL)
            break;

        // bump line number and make sure buffer '\0' terminated
        buffer[MaxLineSize-1] = '\0';

        // decide if line is too long, look for '\n'
        scan = strchr (buffer, '\n');
        if (scan == NULL)
        {   // '\n' not found, line too long!
            error("File %s: line too long at line number %d",
                    scriptpath, line_number);
        }
        *scan = '\0';                   // remove trailing '\n'

        // if comment or blank line, try again
        if (should_skip(buffer))
            continue;

        // decide if line is new test or continuation
        if (isspace(buffer[0]))
        {   // continuation
            // test for continuation without first part of test
            if (head_test == NULL)
                error("Test continuation on first code line of test file!?");

            Command *new_cmds = parse_cmds(buffer);

            last_cmd->next = new_cmds;
            while (last_cmd->next)
                last_cmd = last_cmd->next;
        }
        else
        {   // new test
            Test *new_test = new_Test(line_number, parse_cmds(buffer));

            if (head_test == NULL)
            {   // first test
                last_test = head_test = new_test;
            }
            else
            {   // add to end of Test chain
                last_test->next = new_test;
                last_test = new_test;
            }

            // move 'last_cmd' to end of command chain
            for (last_cmd = last_test->commands;
                    last_cmd->next != NULL;
                    last_cmd = last_cmd->next)
                ;
        }
    }

    printf("\r");

    // close script file
    fclose(fd);

    return head_test;
}


/******************************************************************************
Description : Check that memory values are as they should be.
 Parameters :
    Returns : The number of errors encountered.
   Comments : Expected values shopuld be the global 'MemAllValue' or one of the
            : values in the 'MemValues' plist.
 ******************************************************************************/
int
check_all_mem(void)
{
    int result = 0;

    for (WORD adr = 0; adr < MEM_SIZE; ++adr)
    {
        WORD value = mem_get(adr, false);
        WORD expected;

        if (get_mem_plist(adr, &expected))
        {
            if (expected != value)
            {
                vlog("Memory at %07o changed, is %07o, should be %07o",
                        adr, value, expected);
                result += 1;
            }
        }
        else
        {
            if (value != MemAllValue)
            {
                vlog("Memory at %07o changed, is %07o, should be %07o",
                        adr, value, MemAllValue);
                result += 1;
            }
        }
    }

    return result;
}

/******************************************************************************
Description : Check that a register value is as it should be.
 Parameters : reg - register name
    Returns : The number of errors encountered.
   Comments : Expected values should be the value in 'RegValues' plist.
 ******************************************************************************/
int
check_reg(char *reg)
{
    WORD expect;
    WORD value;

    if (STREQ(reg, "AC")) value = cpu_get_AC();
    else if (STREQ(reg, "L")) value = cpu_get_L();
    else if (STREQ(reg, "PC")) value = cpu_get_PC();
    else if (STREQ(reg, "DS")) value = cpu_get_DS();
    else
    {
        vlog("check_reg: bad register name '%s'", reg);
        return 1;
    }

    if (get_reg_plist(reg, &expect))
    {
        if (value != expect)
        {
            vlog("Register %s has bad value, expected %07o got %07o",
                    reg, expect, value);
            return 1;
        }
    }

    return 0;
}


/******************************************************************************
Description : Check that register values are as they should be.
 Parameters :
    Returns : The number of errors encountered.
   Comments : Expected values should be the value in 'RegValues' plist.
 ******************************************************************************/
int
check_all_regs(void)
{
    int result = 0;

    result += check_reg("AC");
    result += check_reg("L");
    result += check_reg("PC");
    result += check_reg("DS");

    return result;
}

/******************************************************************************
Description : Run all commands in one test line.
 Parameters : test - pointer to a Test struct
    Returns : The number of errors encountered.
   Comments :
 ******************************************************************************/
int
run_one_test(Test *test)
{
    int error = 0;
    char buffer[256];

    // set up memory/register value data structures
    MemValues = PlistCreate();
    RegValues = PlistCreate();

    // set memory and registers to known initial values
    MemAllValue = InitMemValue;
    mem_clear(InitMemValue);

    RegAllValue = InitRegValue;
    cpu_set_AC(InitRegValue);
    cpu_set_L(InitRegValue & 1);
    cpu_set_PC(InitRegValue);
    cpu_set_DS(InitRegValue);

    UsedCycles = 0;

    ptrptp_reset();

    trace_open();

    for (Command *cmd = test->commands; cmd; cmd = cmd->next)
    {
        char *opcode = cmd->opcode;
        char *fld1 = cmd->field1;
        char *fld2 = cmd->field2;

        if (fld2)
            sprintf(buffer, "%s %s %07o%s",
                    opcode, fld1, str2word(fld2), (cmd->orig2) ? cmd->orig2 : "");
        else
            sprintf(buffer, "%s %s", opcode, fld1);
        trace_delim(buffer);

        if (STREQ(opcode, "SETREG"))
            error += setreg(fld1, fld2);
        else if (STREQ(opcode, "SETMEM"))
            error += setmem(fld1, fld2);
        else if (STREQ(opcode, "RUN"))
            error += run(fld1, fld2);
        else if (STREQ(opcode, "RUNUNTIL"))
            error += rununtil(fld1, fld2);
        else if (STREQ(opcode, "CHECKCYCLES"))
            error += checkcycles(fld1, fld2);
        else if (STREQ(opcode, "CHECKREG"))
            error += checkreg(fld1, fld2);
        else if (STREQ(opcode, "CHECKMEM"))
            error += checkmem(fld1, fld2);
        else if (STREQ(opcode, "ALLREG"))
            error += allreg(fld1, fld2);
        else if (STREQ(opcode, "ALLMEM"))
            error += allmem(fld1, fld2);
        else if (STREQ(opcode, "bootrom"))
            error += allmem(fld1, fld2);
        else if (STREQ(opcode, "CHECKRUN"))
            error += checkrun(fld1, fld2);
        else if (STREQ(opcode, "CHECKDCPU"))
            error += checkdcpu(fld1, fld2);
        else if (STREQ(opcode, "CHECKCPU"))
            error += checkcpu(fld1, fld2);
        else if (STREQ(opcode, "MOUNT"))
            error += mount(fld1, fld2);
        else if (STREQ(opcode, "DISMOUNT"))
            error += dismount(fld1, fld2);
        else if (STREQ(opcode, "CHECKFILE"))
            error += checkfile(fld1, fld2);
        else
        {
            printf("Unrecognized operation '%s' at line %d\n",
                    opcode, test->line_number);
            error += 1;
        }
    }

    trace_close();

    // now check all memory and regs for changes
    error += check_all_mem();
    error += check_all_regs();

    // destroy any created data structures
    MemValues = PlistDestroy(MemValues);
    RegValues = PlistDestroy(RegValues);

    return error;
}


/******************************************************************************
Description : Run tests and collect number of errors.
 Parameters : test - pointer to a chain if Test structs
    Returns : The number of errors encountered.
   Comments :
 ******************************************************************************/
int
run_tests(Test *test)
{
    int errors = 0;
    int one_test_errors = 0;
    char buffer[1024];
    int loop_count = 0;

    while (test)
    {
        // some indication of progress
        show_progress(test->line_number);

        // echo test to log
        sprintf(buffer, "%03d", test->line_number);
        LogPrefix = new_String(buffer);

        strcpy(buffer, "");

        for (Command *cscan = test->commands; cscan != NULL; cscan = cscan->next)
        {
            sprintf(buffer+strlen(buffer), " %s", cscan->opcode);

            if (cscan->field1)
                sprintf(buffer+strlen(buffer), " %s", cscan->field1);

            if (cscan->field2)
                sprintf(buffer+strlen(buffer), " %07o", str2word(cscan->field2));

            if (cscan->orig2)
                sprintf(buffer+strlen(buffer), " %s", cscan->orig2);

            sprintf(buffer+strlen(buffer), ";");
        }

        one_test_errors = run_one_test(test);
        if (one_test_errors)
        {
            LogPrefix = NULL;
            vlog(buffer+1);
            vlog("");
        }
        errors += one_test_errors;

        loop_count += 1;
        test = test->next;
    }

    printf("\n");
    fflush(stdout);

    return errors;
}


/******************************************************************************
Description : Function to execute test script.
 Parameters : script - path to script file to execute
    Returns :
   Comments :
 ******************************************************************************/
int
execute(char *script)
{
    Test *test = NULL;                      // chain of test commands

    // get test commands into massaged form in memory
    test = parse_script(script);

#ifdef JUNK
    // DEBUG - print contents of 'test'
    for (Test *tscan = test; tscan != NULL; tscan = tscan->next)
    {
        printf("%03d: ", tscan->line_number);

        for (Command *cscan = tscan->commands; cscan != NULL; cscan = cscan->next)
            printf("%s %s %s; ", cscan->opcode, cscan->field1, cscan->field2);

        printf("\n");
        fflush(stdout);
    }
#endif

    // execute tests
    return run_tests(test);
}


int
main(int argc, char *argv[])
{
    int errors = 0;
    int option = 0;
    char *script = NULL;
    FILE *script_fd;

    // check parameters
    while ((option = getopt(argc, argv, "h")) != -1)
    {
        switch (option)
        {
            case 'h':
                usage(NULL);
                exit(EXIT_SUCCESS);
            default:
                usage(NULL);
                exit(EXIT_FAILURE);
        }
    }

    if (optind >= argc)
    {
        usage("Expected test instructions filename after options");
        exit(EXIT_FAILURE);
    }

    // get filename and make sure it's there
    script = argv[optind];
    if ((script_fd = fopen(script, "rb")) == NULL)
        error("File %s doesn't exist or isn't readable: %d\n",
                script, errno);
    fclose(script_fd);

    errors = execute(script);

    printf("%d errors found\n", errors);

    return errors;
}

