/*
 * Test the CPU implementation.
 *
 * We implement a small interpreter to test the CPU.  The test code is read in
 * from a file:
 *
 *    # LAW
 *    setreg ac 012345; setreg l 1; setreg pc 0100; setmem 0100 [LAW 0]; RUN; checkcycles 1; checkreg pc 0101; checkreg ac 0
 *    setreg ac 012345; setreg l 0; setmem 0100 [LAW 0]; RUN 0100
 *            checkcycles 1; checkreg pc 0101; checkreg ac 0
 *
 * The instructions are delimited by ';' characters.  A line beginning with a
 * white space is a continuation of the previous line.
 * Lines with '#' in column 1 are comments.
 *
 * The test instructions are:
 *     setreg <name> <value>
 *         where <name> is one of AC, L, PC or DS, value is any value
 *         (all registers are set to 0 initially)
 *
 *     setmem <addr> <value>
 *         where <addr> is an address and value is any value OR
 *         [<instruction>] where the value is the assembled opcode
 *
 *     run [<addr>]
 *         execute one instruction, if optional <addr> is used PC := addr before
 *
 *     checkcycles <number>
 *         check number of executed cycles is <number>
 *
 *     checkreg <name> <value>
 *         check register (AC, L, PC or DS) has value <value>
 *
 *     checkmem <addr> <value>
 *         check that memory at <addr> has <value>
 *
 *     allreg <value>
 *         sets all registers to <value>
 *         a "allreg 0" is assumed before each test
 *
 *     allmem <value>
 *         sets all of memory to <value>
 *         a "allmem 0" is assumed before each test
 *
 * In addition, all of memory is checked for changed values after execution
 * except where an explicit "checkmem <addr> <value>" has been performed.
 * Additionally, registers that aren't explicitly checked are tested to make
 * sure they didn't change.
 *
 * If a test line finds no error, just print the fully assembled test line.
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
#include "error.h"
#include "log.h"
#include "plist.h"


// string comparison macro
#define STREQ(a, b) (strcmp((a), (b)) == 0)

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


void
show_progress(void)
{
    static int count = 0;
    int index = count++ % NUMELTS(Progress);
    char *p = Progress[index];

    printf(p);
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
// The following functions are the DSL functions.
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
Description : Set the display ON or OFF.
 Parameters : state - string containing 'on' or 'off'
            : var2  - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
setd(char *state, char *var2)
{
    if (STREQ(state, "ON"))
        dcpu_start();
    else if (STREQ(state, "OFF"))
        dcpu_stop();
    else
    {
        vlog("setd: bad state: %s", state);
        return 1;
    }

    return 0;
}


/******************************************************************************
Description : Set a memory cell to a value;
 Parameters : addr - address of memory cell (string)
            : fld2 - value to put into cell (string)
    Returns : The number of errors encountered (0 or 1).
   Comments : Sets globals used to check after execution.
 ******************************************************************************/
int
setmem(char *addr, char *fld2)
{
    WORD address = str2word(addr);
    WORD value = str2word(fld2);

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
Description : Run one instruction on the CPU.
 Parameters : addr - address of memory cell (string, may be NULL)
            : fld2 - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
run_one(char *addr, char *fld2)
{

    // if given address run from that address, else use PC contents
    if (addr)
        cpu_set_PC(str2word(addr));

    cpu_start();
    UsedCycles = cpu_execute_one();

    return 0;
}


/******************************************************************************
Description : Check that the number of cycles used is as expected.
 Parameters : cycles - address of memory cell (string)
            : var2   - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkcycles(char *cycles, char *fld2)
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
Description : Check that the display is in the correct state.
 Parameters : state  - string holding expected display state ('on' or 'off)
            : unused - unused
    Returns : The number of errors encountered (0 or 1).
   Comments :
 ******************************************************************************/
int
checkd(char *state, char *unused)
{
    if ((STREQ(state, "on")) && !DisplayOn)
    {
        vlog("Display CPU run state is %s, should be 'ON'",
                (DisplayOn ? "ON": "OFF"));
        return 1;
    }
    else if ((STREQ(state, "off")) && DisplayOn)
    {
        vlog("DCPU run state is %s, should be 'OFF'",
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
    bool cpu_state = cpu_get_state();

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
    Returns :
   Comments : We already have an assembler, so we just reuse it.  Generate an
            : ASM file, assemble it and pick out the opcode from the LST file.
 ******************************************************************************/
WORD
assemble(WORD addr, char *opcode)
{
    FILE *fd;
    char buffer[128];
    WORD result;

    // create the ASM file
    fd = fopen(AsmFilename, "wb");
    fprintf(fd, "\torg\t%07o\n", addr);
    fprintf(fd, "\t%s\n", opcode);
    fprintf(fd, "\tend\n");
    fclose(fd);

    // assemble the file
    sprintf(buffer, "../iasm/iasm -l %s %s", LstFilename, AsmFilename);
    if (system(buffer) == -1)
        error("Error doing: %s", buffer);

    // read LST file for opcode on second line
    fd = fopen(LstFilename, "rb");
    if (fgets(buffer, sizeof(buffer), fd) == NULL)
        error("Error reading %s", LstFilename);
    if (fgets(buffer, sizeof(buffer), fd) == NULL)
        error("Error reading %s", LstFilename);
    if (sscanf(buffer, "%o", &result) != 1)
        error("Badly formatted assembler output: %s", buffer);
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
    char tmpbuff[16];


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

        // field2
        while (*scan && isspace(*scan)) // skip leading space
            ++scan;
        if (*scan)
        {
            field2 = scan;
            if (*field2 == '[')
            {   // assembler field
                orig2 = new_String(field2);
                ++field2;
                while (*scan && !(*scan == ']'))
                    ++scan;
                *scan = '\0';
                WORD v = str2word(field1);
                v = assemble(str2word(field1), field2);
                sprintf(tmpbuff, "%d", v);
                field2 = tmpbuff;
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
        // some indication of progress
        show_progress();

        // NULL fill buffer so we can tell if line too long
        memset(buffer, (char) NULL, sizeof(buffer));

        // get next line, break out of loop on end of file
        if (fgets(buffer, sizeof(buffer), fd) == NULL)
            break;

        // bump line number and make sure buffer '\0' terminated
        ++line_number;
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
//    char buffer[256];

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

    for (Command *cmd = test->commands; cmd; cmd = cmd->next)
    {
        char *opcode = cmd->opcode;
        char *fld1 = cmd->field1;
        char *fld2 = cmd->field2;

#ifdef JUNK
        if (fld2)
            sprintf(buffer, "%s %s %07o%s",
                    opcode, fld1, str2word(fld2), (cmd->orig2) ? cmd->orig2 : "");
        else
            sprintf(buffer, "%s %s", opcode, fld1);
        LogPrefix = new_String(buffer);
#endif

        if (STREQ(opcode, "SETREG"))
            error += setreg(fld1, fld2);
        else if (STREQ(opcode, "SETMEM"))
            error += setmem(fld1, fld2);
        else if (STREQ(opcode, "RUN"))
            error += run_one(fld1, fld2);
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
        else if (STREQ(opcode, "CHECKRUN"))
            error += checkrun(fld1, fld2);
        else if (STREQ(opcode, "SETD"))
            error += setd(fld1, fld2);
        else if (STREQ(opcode, "CHECKD"))
            error += checkd(fld1, fld2);
        else
        {
            printf("Unrecognized operation '%s' at line %d\n",
                    opcode, test->line_number);
            error += 1;
        }
    }

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
run(Test *test)
{
    int errors = 0;
    int one_test_errors = 0;
    char buffer[1024];
    int loop_count = 0;

    while (test)
    {
        // some indication of progress
        show_progress();

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

    printf("\r");
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
    return run(test);
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

