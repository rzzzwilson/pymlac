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
 * TAB character is a continuation of the previous line.
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
#include "memory.h"
#include "error.h"


// constants
const char *LstFilename = "_#TEST#_.lst";   // LST filename
const char *AsmFilename = "_#TEST#_.asm";   // ASM filename

const int MaxLineSize = 4096;               // max length of one script line

// command structures
typedef struct _Command
{
    struct _Command *next;
    char *opcode;
    char *field1;
    char *field2;
} Command;

typedef struct _Test
{
    struct _Test *next;
    int line_number;
    Command *commands;
} Test;


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

    result->next = NULL;
    result->field1 = NULL;
    result->field2 = NULL;

    return result;
}


/******************************************************************************
Description : Constructor for a Command struct.
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
char *
new_String(char *str)
{
    char *result = (char *) malloc(strlen(str)+1);
    strcpy(result, str);
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
   Comments : We generate an ASM file, assemble it and pick out the binary
            : opcode from the LST file.
 ******************************************************************************/
int
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

    return result;   
}
   

/******************************************************************************
Description : Decide if buffer kine should be skipped.
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

    // find start and end of opcode
    while (*scan && isspace(*scan))
        ++scan;
    opcode = scan;
    while (*scan && !isspace(*scan))
        ++scan;
    *scan = '\0';
    ++scan;

    // start/end of field1 (if there)
    while (*scan && isspace(*scan))
        ++scan;
    if (*scan)
    {
        field1 = scan;
        while (*scan && !isspace(*scan))
            ++scan;
        *scan = '\0';
        ++scan;

        // field2
        while (*scan && isspace(*scan))
            ++scan;
        if (*scan)
        {
            field2 = scan;
            if (*field2 == '[')
            {
                ++field2;
                while (*scan && !(*scan == ']'))
                    ++scan;
                *scan = '\0';
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

    return result;
}


/******************************************************************************
Description : Read the command buffer and create a chain of Command structs.
 Parameters : scriptpath - script filename
    Returns : Pointer to a chain of Test structs.
   Comments : 
 ******************************************************************************/
Command *
parse_cmds(char *scan)
{
    Command *result = NULL;
    Command *last_result = NULL;
    char *end_cmd = NULL;
    Command *new_cmd = NULL;

    printf("parse_cmds: scan->%s\n", scan);

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

    printf("parse_cmds: before parse_one_cmd(), scan->%s\n", scan);

        new_cmd = parse_one_cmd(scan);

    printf("parse_cmds: after parse_one_cmd(), result=%p, last_result=%p, new_cmd=%p\n", result, last_result, new_cmd);
    fflush(stdout);

        if (result == NULL)
        {
            result = new_cmd;
            last_result = result;
        }
        else
        {
            printf("parse_cmds: last_result->next=%p\n", last_result->next);
            last_result->next = new_cmd;
            last_result = new_cmd;
        }

        scan = new_scan;
        printf("parse_cmds: bottom of loop, scan=%p\n", scan);
        fflush(stdout);
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

        // DEBUG
        printf("%03d: %s\n", line_number, buffer);

        // decide if line is new test or continuation
        if (isspace(buffer[0]))
        {   // continuation
            printf("CONTINUE\n");

            // test for continuation without first part of test
            if (head_test == NULL)
                error("Test continuation on first code line of test file!?");

            Command *new_cmds = parse_cmds(buffer);
            printf("Point 1, last_cmd=%p, last_cmd->next=%p\n", last_cmd, last_cmd->next); fflush(stdout);

            last_cmd->next = new_cmds;
            printf("Point 2\n"); fflush(stdout);
            while (last_cmd->next)
                last_cmd = last_cmd->next;
            printf("Point 3\n"); fflush(stdout);
            printf("END CONTINUE\n");
        }
        else
        {   // new test
            printf("NEW\n");

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
            for (last_cmd = last_test->commands; last_cmd->next != NULL; last_cmd = last_cmd->next)
                ;

            printf("END NEW, last_cmd=%p, last_cmd->next=%p\n", last_cmd, last_cmd->next);
        }
        fflush(stdout);
    }

    // close script file
    fclose(fd);

    return head_test;
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
    printf("execute: ENTER\n");

    Test *test = NULL;                      // chain of test commands

    // get test commands into massaged form in memory
    test = parse_script(script);

    printf("execute: test=%p\n", test);

    // DEBUG - print contents of 'test'
    for (Test *tscan = test; tscan != NULL; tscan = tscan->next)
    {
        printf("%03d: ", tscan->line_number);

        for (Command *cscan = tscan->commands; cscan != NULL; cscan = cscan->next)
            printf("%s %s %s; ", cscan->opcode, cscan->field1, cscan->field2);

        printf("\n");
        fflush(stdout);
    }

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
    if ((script_fd = fopen(script, "r")) == NULL)
    {
        error("File %s doesn't exist or isn't readable: %d\n",
                script, errno);
    }

    errors = execute(script);

    printf("%d errors found\n", errors);

    return 0;
}


#ifdef JUNK


import os

from Globals import *
import MainCPU
import Memory
import Trace

import log
log = log.Log('test_CPU.log', log.Log.DEBUG)


class TestCPU(object):

    # temporary assembler file and listfile prefix
    AsmFilename = '_#ASM#_'


    def __init__(self):
        """Initialize the test."""

        pass

    def assemble(self, addr, opcode):
        """Assemble a single instruction, return opcode."""

        # create ASM file with instruction
        with open(self.AsmFilename+'.asm', 'wb') as fd:
            fd.write('\torg\t%07o\n' % addr)
            fd.write('\t%s\n' % opcode[1:-1])
            fd.write('\tend\n')

        # now assemble file
        #cmd = '../iasm/iasm -l %s.lst %s.asm >xyzzy 2>&1' % (self.AsmFilename, self.AsmFilename)
        cmd = '../iasm/iasm -l %s.lst %s.asm' % (self.AsmFilename, self.AsmFilename)
        res = os.system(cmd)

        # read the listing file to get assembled opcode (second line)
        with open(self.AsmFilename+'.lst', 'rb') as fd:
            lines = fd.readlines()
        line = lines[1]
        (opcode, _) = line.split(None, 1)

        return int(opcode, base=8)


    def setreg(self, name, value):
        """Set register to a value.

        Remember value to check later.
        """

        self.reg_values[name] = value

        if name == 'ac':
            self.cpu.AC = value
        elif name == 'l':
            self.cpu.L = value & 1
        elif name == 'pc':
            self.cpu.PC = value
        elif name == 'ds':
            self.cpu.DS = value
        else:
            raise Exception('setreg: bad register name: %s' % name)

    def setmem(self, addr, value):
        """Set memory location to a value."""

        if isinstance(value, basestring):
            log.debug('setmem: addr=%s, value=%s' % (oct(addr), value))
        else:
            log.debug('setmem: addr=%s, value=%s' % (oct(addr), oct(value)))

        # check if we must assemble var2
        if isinstance(value, basestring) and value[0] == '[':
            # assemble an instruction
            value = self.assemble(addr, value)
            log.debug('setmem: assembled opcode=%07o' % value)

        self.mem_values[addr] = value
        log.debug('setmem: After, MemValues=%s' % str(self.mem_values))

        self.memory.put(value, addr, False)
        log.debug('setmem: After, Memory at %07o is %07o' % (addr, self.memory.fetch(addr, False)))

    def allmem(self, value, ignore=None):
        """Set all of memory to a value.

        Remember value to check later.
        """

        log.debug('allmem: setting memory to %07o' % value)

        self.mem_all_value = value

        for mem in range(MEMORY_SIZE):
            self.memory.put(value, mem, False)

    def allreg(self, value):
        """Set all registers to a value."""

        self.reg_all_value = value

        self.cpu.AC = value
        self.cpu.L = value & 1
        self.cpu.PC = value
        self.cpu.DS = value

    def check_all_mem(self):
        """Check memory for unwanted changes."""

        result = []

        for mem in range(MEMORY_SIZE):
            value = self.memory.fetch(mem, False)
            if mem in self.mem_values:
                if value != self.mem_values[mem]:
                    result.append('Memory at %07o changed, is %07o, should be %07o'
                                  % (mem, value, self.mem_values[mem]))
            else:
                if value != self.mem_all_value:
                    print('mem: %s, value: %s, self.mem_all_value: %s'
                          % (str(type(mem)), str(type(value)), str(type(self.mem_all_value))))
                    result.append('Memory at %07o changed, is %07o, should be %07o'
                                  % (mem, value, self.mem_all_value))

    def check_all_regs(self):
        """Check registers for unwanted changes."""

        result = []

        if 'ac' in self.reg_values:
            if self.cpu.AC != self.reg_values['ac']:
                result.append('AC changed, is %07o, should be %07o'
                              % (self.cpu.AC, self.reg_values['ac']))
        else:
            if self.cpu.AC != self.reg_all_value:
                result.append('AC changed, is %07o, should be %07o'
                              % (self.cpu.AC, self.reg_all_value))

        if 'l' in self.reg_values:
            if self.cpu.L != self.reg_values['l']:
                result.append('L changed, is %02o, should be %02o'
                              % (self.cpu.L, self.reg_values['l']))
        else:
            if self.cpu.L != self.reg_all_value & 1:
                result.append('L changed, is %02o, should be %02o'
                              % (self.cpu.L, self.reg_all_value & 1))

        if 'pc' in self.reg_values:
            if self.cpu.PC != self.reg_values['pc']:
                result.append('PC changed, is %07o, should be %07o'
                              % (self.cpu.PC, self.reg_values['pc']))
        else:
            if self.cpu.PC != self.reg_all_value:
                result.append('PC changed, is %07o, should be %07o'
                              % (self.cpu.PC, self.reg_all_value))

        if 'ds' in self.reg_values:
            if self.cpu.DS != self.reg_values['ds']:
                result.append('DS changed, is %07o, should be %07o'
                              % (self.cpu.DS, self.reg_values['ds']))
        else:
            if self.cpu.DS != self.reg_all_value:
                result.append('DS changed, is %07o, should be %07o'
                              % (self.cpu.DS, self.reg_all_value))

        return result

    def checkreg(self, reg, value):
        """Check register is as it should be."""

        if reg == 'ac':
            self.reg_values[reg] = self.cpu.AC
            if self.cpu.AC != value:
                return 'AC wrong, is %07o, should be %07o' % (self.cpu.AC, value)
        elif reg == 'l':
            self.reg_values[reg] = self.cpu.L
            if self.cpu.L != value:
                return 'L wrong, is %02o, should be %02o' % (self.cpu.L, value)
        elif reg == 'pc':
            self.reg_values[reg] = self.cpu.PC
            if self.cpu.PC != value:
                return 'PC wrong, is %07o, should be %07o' % (self.cpu.PC, value)
        elif reg == 'ds':
            self.reg_values[reg] = self.cpu.DS
            if self.cpu.DS != value:
                return 'DS wrong, is %07o, should be %07o' % (self.cpu.DS, value)
        else:
            raise Exception('checkreg: bad register name: %s' % name)

    def checkmem(self, addr, value):
        """Check a memory location is as it should be."""

        self.mem_values[addr] = value
        log.debug('checkmem: After, MemValues=%s' % str(self.mem_values))

        memvalue = self.memory.fetch(addr, False)
        if memvalue != value:
            return 'Memory wrong at address %07o, is %07o, should be %07o' % (addr, memvalue, value)

    def checkcycles(self, cycles, var2=None):
        """Check that opcode cycles used is correct."""

        if cycles != self.used_cycles:
            return 'Opcode used %d cycles, expected %d' % (self.used_cycles, cycles)

    def run(self, addr, var2):
        """Execute instruction."""

        if addr is not None:
            # force PC to given address
            self.setreg('pc', addr)

        self.used_cycles = self.cpu.execute_one_instruction()

    def checkrun(self, state, var2):
        """Check CPU run state is as desired."""

        if str(self.cpu.running).lower() != state:
            return 'CPU run state is %s, should be %s' % (str(self.cpu.running), str(state))

    def setd(self, state, var2):
        """Set display state."""

        if state == 'on':
            self.display_state = True
        elif state == 'off':
            self.display_state = False
        else:
            raise Exception('setd: bad state: %s' % str(state))

    def checkd(self, state, var2):
        """Check display state is as expected."""

        if state == 'on' and self.display_state is not True:
            return 'DCPU run state is %s, should be True' % str(self.display_state)
        if state == 'off' and self.display_state is True:
            return 'DCPU run state is %s, should be False' % str(self.display_state)

    def debug_operation(self, op, var1, var2):
        """Write operation to log file."""

        if var1:
            if var2:
                log.debug('Operation: %s %s %s' % (op, var1, var2))
            else:
                log.debug('Operation: %s %s' % (op, var1))
        else:
            log.debug('Operation: %s' % op)

    def execute(self, test, filename):
        """Execute test string in 'test'."""

        # set globals
        self.reg_values = {}
        self.mem_values = {}
        #self.reg_all_value = {}
        #self.mem_all_value = {}
        self.reg_all_value = 0
        self.mem_all_value = 0

        result = []

        self.memory = Memory.Memory()
        self.cpu = MainCPU.MainCPU(self.memory, None, None, None, None, None, None, None)
        self.cpu.running = True
        self.display_state = False

        trace_filename = filename + '.trace'
        Trace.init(trace_filename, self.cpu, None)

        # clear registers to 0 first
        self.allreg(0)

        # interpret the test instructions
        instructions = test.split(';')
        for op in instructions:
            fields = op.split(None, 2)
            op = fields[0].lower()
            try:
                var1 = fields[1].lower()
            except IndexError:
                var1 = None
            try:
                var2 = fields[2].lower()
            except IndexError:
                var2 = None

            self.debug_operation(op, var1, var2)

            # change var strings into numeric values
            if var1 and var1[0] in '0123456789':
                if var1[0] == '0':
                    var1 = int(var1, base=8)
                else:
                    var1 = int(var1)
                var1 &= 0177777

            if var2 and var2[0] in '0123456789':
                if var2[0] == '0':
                    var2 = int(var2, base=8)
                else:
                    var2 = int(var2)
                var2 &= 0177777

            if op == 'setreg':
                r = self.setreg(var1, var2)
            elif op == 'setmem':
                r = self.setmem(var1, var2)
            elif op == 'run':
                r = self.run(var1, var2)
            elif op == 'checkcycles':
                r = self.checkcycles(var1, var2)
            elif op == 'checkreg':
                r = self.checkreg(var1, var2)
            elif op == 'checkmem':
                r = self.checkmem(var1, var2)
            elif op == 'allreg':
                r = self.allreg(var1, var2)
            elif op == 'allmem':
                r = self.allmem(var1, var2)
            elif op == 'checkrun':
                r = self.checkrun(var1, var2)
            elif op == 'setd':
                r = self.setd(var1, var2)
            elif op == 'checkd':
                r = self.checkd(var1, var2)
            else:
                raise Exception("Unrecognized operation '%s' in: %s" % (op, test))

            if r is not None:
                result.append(r)

        # now check all memory and regs for changes
        r = self.check_all_mem()
        if r:
            result.append(r)

        r = self.check_all_regs()
        if r:
            result.extend(r)

        if result:
            print(test)
            print('\t' + '\n\t'.join(result))

        self.memdump('core.txt', 0, 0200)

    def memdump(self, filename, start, number):
        """Dump memory from 'start' into 'filename', 'number' words dumped."""

        with open(filename, 'wb') as fd:
            for addr in range(start, start+number, 8):
                a = addr
                llen = min(8, start+number - addr)
                line = '%04o  ' % addr
                for _ in range(llen):
                    line += '%06o ' % self.memory.fetch(a, False)
                    a += 1
                fd.write('%s\n' % line)

    def main(self, filename):
        """Execute CPU tests from 'filename'."""

        log.debug("Running test file '%s'" % filename)

        # get all tests from file
        with open(filename, 'rb') as fd:
            lines = fd.readlines()

        # read lines, join continued, get complete tests
        tests = []
        test = ''
        for line in lines:
            line = line[:-1]        # strip newline
            if not line:
                continue            # skip blank lines

            if line[0] == '#':      # a comment
                continue

            if line[0] == '\t':     # continuation
                if test:
                    test += '; '
                test += line[1:]
            else:                   # beginning of new test
                if test:
                    tests.append(test)
                test = line

        # flush last test
        if test:
            tests.append(test)

        # now do each test
        for test in tests:
            log.debug('Executing test: %s' % test)
            self.execute(test, filename)

################################################################################

if __name__ == '__main__':
    import sys
    import getopt

    def usage(msg=None):
        if msg:
            print('*'*60)
            print(msg)
            print('*'*60)
        print(__doc__)

    try:
        (opts, args) = getopt.gnu_getopt(sys.argv, "h", ["help"])
    except getopt.GetoptError:
        usage()
        sys.exit(10)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            usage()
            sys.exit(0)

    if len(args) != 2:
        usage()
        sys.exit(10)

    filename = args[1]
    try:
        f = open(filename)
    except IOError:
        print("Sorry, can't find file '%s'" % filename)
        sys.exit(10)
    f.close()

    test = TestCPU()
    test.main(filename)
#endif
