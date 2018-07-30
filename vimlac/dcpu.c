/******************************************************************************\
 *                                dcpu.c                                      *
 *                                -------                                     *
 *                                                                            *
 *  This file is used to decode and execute a display processor instruction.  *
 *                                                                            *
\******************************************************************************/

#include "vimlac.h"
#include "dcpu.h"
#include "memory.h"
#include "display_pbm.h"
#include "log.h"
#include "trace.h"


/******
 * Constants, etc.
 ******/

#define MSBBITS     6
#define LSBBITS     5

#define MSBMASK     03740
#define LSBMASK     037

// full 11 bits of display addressing
#define DMASK       03777
// AC bits that set DX or DY
#define BITS10      01777

#define DMSB        03740

#define DLSB        037

// display CPU constants - modes
#define MODE_NORMAL 0
#define MODE_DEIM   1

// full 11 bits of display addressing
#define DMASK       03777
// AC bits that set DX or DY
#define BITS10      01777
#define DMSB        03740
#define DLSB        037

/******
 * Emulated registers, state, memory, etc.
 ******/

static WORD DPC = 0;                            // the display PC
static WORD Prev_DPC;                           // the *previous* display PC
static WORD DRS[] = {0, 0, 0, 0, 0, 0, 0, 0};   // display CPU stack
static int DRSindex;                            //
static int DX;                                  //
static int DY;                                  //
static float DScale = 4;                        // display scale (1, 2, 4, 8)
int DIB = 0;                                    // ????
static BYTE Mode = MODE_NORMAL;                 // DEIM mode
static bool Running = false;                    // true if display processor is running

static char DEIM_result[100];                   // holds DEIM_decode() result


/******************************************************************************
Description : Functions to get/set various registers.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/

WORD
dcpu_get_PC(void)
{
    return DPC;
}


WORD
dcpu_get_prev_PC(void)
{
    return Prev_DPC;
}


void
dcpu_set_PC(WORD value)
{
    DPC = value;
}


void
dcpu_set_DRSindex(int value)
{
    DRSindex = value;
}


/******************************************************************************
Description : Function to handle unrecognized instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static void
illegal(void)
{
    WORD oldPC = Prev_DPC & MEMMASK;

    error("INTERNAL ERROR: "
          "unexpected main processor opcode %06.6o at address %06.6o",
          mem_get(oldPC, false), oldPC);
}


/******************************************************************************
Description : Decode a DEIM byte into human text.
 Parameters : byte - the DEIM byte to decode
    Returns : A string that describes the DEIM byte
   Comments : Uses the static buffer "DEIM_result".
 ******************************************************************************/
char *
DEIMdecode(BYTE byte)
{
    // empty the result buffer
    char *bptr = DEIM_result;
    *bptr = '\0';

    // now decode the DEIM byte
    if (byte & 0x80)
    {
        if (byte & 0x40)
        {
            strcat(bptr, "B");
            *++bptr = '\0';
        }
        else
        {
            strcat(bptr, "D");
            *++bptr = '\0';
        }

        if (byte & 0x20)
        {
            strcat(bptr, "-");
            *++bptr = '\0';
        }

        sprintf(bptr, "%d", (byte >> 3) & 0x03);
        bptr = DEIM_result + strlen(DEIM_result);

        if (byte & 0x04)
        {
            strcat(bptr, "-");
            *++bptr = '\0';
        }

        sprintf(bptr, "%d", byte & 0x03);
        bptr = DEIM_result + strlen(DEIM_result);
    }
    else
    {
        if (byte == 0111)
        {
            strcat(bptr, "N");
            *++bptr = '\0';
        }
        else if (byte == 0151)
        {
            strcat(bptr, "R");
            *++bptr = '\0';
        }
        else if (byte == 0171)
        {
            strcat(bptr, "F");
            *++bptr = '\0';
        }
        else if (byte == 0200)
        {
            strcat(bptr, "P");
            *++bptr = '\0';
        }
        else
        {
            sprintf(bptr, "A%03o", byte);
            bptr = DEIM_result + strlen(DEIM_result);
        }
    }

    return DEIM_result;
}


/******************************************************************************
Description : Execute a DEIM instruction byte.
 Parameters : byte - the DEIM byte to decode
            : last - 'true' if the last byte in a word
    Returns : A trace string that describes the DEIM byte
   Comments : 
 ******************************************************************************/

static
char *doDEIMByte(BYTE byte, bool last)
{
    vlog("doDEIMByte: entered, last=%s", last ? "true" : "false");

    char *trace = DEIMdecode(byte);

    if (byte & 0x80)                    // increment mode
    {
        int dx = (byte & 0x18) >> 3;    // extract X/Y deltas
        int dy = (byte & 0x03);

        int prevDX = DX;                // save previous position
        int prevDY = DY;

        if (byte & 0x20)                // get dx sign and move X
        {
            vlog("doDEIMByte: -x move");
            DX -= dx * DScale;
        }
        else
        {
            DX += dx * DScale;
        }

        if (byte & 0x04)                // get dy sign and move Y
        {
            vlog("doDEIMByte: -y move");
            DY -= dy * DScale;
        }
        else
        {
            DY += dy * DScale;
        }

        if (byte & 0x40)                // if beam on
        {
            display_draw(prevDX, prevDY, DX, DY);
        }
    }
    else                                // control instructions
    {
        if (byte & 0x40)                // escape DEIM mode
        {
            Mode = MODE_NORMAL;
        }

        if (byte & 0x20)                // DRJM
        {
            if (DRSindex <= 0)
            {
                illegal();
            }
            DRSindex -= 1;
            DPC = DRS[DRSindex];
        }

        if (byte & 0x10)                // inc X MSB
        {
            DX += (1 << LSBBITS);
        }

        if (byte & 0x08)                // clear X LSB
        {
            DX &= MSBMASK;
        }

        if (byte & 0x02)                // inc Y MSB
        {
            DY += (1 << LSBBITS);
        }

        if (byte & 0x01)                // clear Y LSB
        {
            DY &= MSBMASK;
        }
    }

    vlog("doDEIMByte: finished, trace='%s'", trace);

    return trace;
}


/******************************************************************************
Description : The emulated display CPU instructions.
 Parameters : 
    Returns : The number of display CPU cycles executed.
   Comments : 
 ******************************************************************************/

static
int i_DDXM(void)
{
    DX -= 040;
    trace_dcpu("DDXM");
    return 1;
}

static
int i_DDYM(void)
{
    DY -= 040;
    trace_dcpu("DDYM");
    return 1;
}

static
int i_DEIM(WORD address)
{
    vlog("i_DEIM: entered");

    Mode = MODE_DEIM;
    vlog("i_DEIM: just before doDEIMByte+trace_dcpu");
    trace_dcpu("DEIM %s", doDEIMByte(address & 0377, true));
    vlog("i_DEIM: returning 1");
    return 1;
}

static
int i_DHLT(void)
{
    Running = false;
    trace_dcpu("DHLT");
    return 1;
}

static
int i_DHVC(void)
{
    trace_dcpu("DHVC");
    // TODO: should DO SOMETHING here?
    return 1;
}

static
int i_DIXM(void)
{
    DX += 04000;
    trace_dcpu("DIXM");
    return 1;
}

static
int i_DIYM(void)
{
    DY += 04000;
    trace_dcpu("DIYM");
    return 1;
}

static
int i_DJMP(WORD address)
{
    DPC = MASK_MEM(address + (DIB << 12));
    trace_dcpu("DJMP %04o", address);
    return 1;
}

static
int i_DJMS(WORD address)
{
    if (DRSindex >= 8)
    {
        illegal();
    }
    DRS[DRSindex] = DPC;
    DRSindex += 1;
    DPC = MASK_MEM(address + (DIB << 12));
    trace_dcpu("DJMS %04o", address);
    return 1;
}

static
int i_DLXA(WORD address)
{
    //DX = (address & BITS10) << 1;
    DX = address & BITS10;
    trace_dcpu("DLXA %04o", address);
    return 1;
}
static
int i_DLYA(WORD address)
{
    //DY = (address & BITS10) << 1;
    DY = address & BITS10;
    trace_dcpu("DLYA %04o", address);
    return 1;
}

static
int i_DLVH(WORD word1)
{
    WORD word2 = mem_get(DPC, false);
    DPC = MASK_MEM(DPC + 1);

    WORD word3 = mem_get(DPC, false);
    DPC = MASK_MEM(DPC + 1);

//    WORD dotted = word2 & 040000;
//    WORD beamon = word2 & 020000;
    WORD negx = word3 & 040000;
    WORD negy = word3 & 020000;
    WORD ygtx = word3 & 010000;

    WORD M = word2 & 007777;
    WORD N = word3 & 007777;

    int prevDX = DX;
    int prevDY = DY;

    if (ygtx)                   // M is y, N is x
    {
        if (negx)
            DX -= N;
        else
            DX += N;

        if (negy)
            DY -= M;
        else
            DY += M;
    }
    else                        // M is x, N is y
    {
        if (negx)
            DX -= M;
        else
            DX += M;

        if (negy)
            DY -= N;
        else
            DY += N;

        //display_draw(prevDX, prevDY, DX, DY, dotted);
        display_draw(prevDX, prevDY, DX, DY);
    }

    trace_dcpu("DLVH");
    return 3;
}

static
int i_DRJM(void)
{
    if (DRSindex <= 0)
    {
        illegal();
    }

    DRSindex -= 1;
    DPC = DRS[DRSindex];
    trace_dcpu("DRJM");
    return 1;                   // FIXME check # cycles used
}

static
int i_DSTB(int block)
{
    DIB = block;
    trace_dcpu("DSTB %d", block);
    return 1;
}

static
int i_DSTS(int scale)
{
    if (scale == 0)
        DScale = 0.5;
    else if (scale == 1)
        DScale = 1.0;
    else if (scale == 2)
        DScale = 2.0;
    else if (scale == 3)
        DScale = 3.0;
    else
        illegal();
    trace_dcpu("DSTS %d", scale);
    return 1;                   // FIXME check # cycles used
}

static
int page00(WORD instruction)
{
    int cycles = 0;

    if (instruction == 000000)                  // DHLT
        cycles = i_DHLT();
    else if (instruction == 004000)             // DNOP
    {
        cycles = 1;
        trace_dcpu("DNOP");
    }
    else if (instruction == 004004)             // DSTS 0
        cycles = i_DSTS(0);
    else if (instruction == 004005)             // DSTS 1
        cycles = i_DSTS(1);
    else if (instruction == 004006)             // DSTS 2
        cycles = i_DSTS(2);
    else if (instruction == 004007)             // DSTS 3
        cycles = i_DSTS(3);
    else if (instruction == 004010)             // DSTB 0
        cycles = i_DSTB(0);
    else if (instruction == 004011)             // DSTB 1
        cycles = i_DSTB(1);
    else if (instruction == 004040)             // DRJM
        cycles = i_DRJM();
    else if (instruction == 004100)             // DDYM
        cycles = i_DDYM();
    else if (instruction == 004200)             // DDXM
        cycles = i_DDXM();
    else if (instruction == 004400)             // DIYM
        cycles = i_DIYM();
    else if (instruction == 005000)             // DIXM
        cycles = i_DIXM();
    else if (instruction == 006000)             // DHVC
        cycles = i_DHVC();
    else
        illegal();

    return cycles;
}

/******************************************************************************
Description : Function to execute one display processor instruction.
 Parameters : 
    Returns : The number of display CPU cycles executed.
   Comments : 
 ******************************************************************************/
int
dcpu_execute_one(void)
{
    vlog("dcpu_execute_one: entered");

    if (!Running)
    {
        return 0;
    }

    //WORD dot = DPC;
    WORD instruction = mem_get(DPC, false);

    DPC = MASK_MEM(DPC + 1);

    if (Mode == MODE_DEIM)
    {
        static char tmp_buff[100];

        strcpy(tmp_buff, doDEIMByte(instruction >> 8, false));
        vlog("dcpu_execute_one: after first doDEIMByte()");

        if (Mode == MODE_DEIM)
        {
            strcat(tmp_buff, ",");
            strcat(tmp_buff, doDEIMByte(instruction & 0xff, true));
            vlog("dcpu_execute_one: after second doDEIMByte()");
        }

        trace_dcpu("INC  %s", tmp_buff);

        return 1;
    }

    WORD opcode = instruction >> 12;
    WORD address = instruction & 07777;

    if (opcode == 000)
    {
        return page00(instruction);
    }
    else if (opcode == 001)
    {
        return i_DLXA(address);
    }
    else if (opcode == 002)
    {
    return i_DLYA(address);
    }
    else if (opcode == 003)
    {
        vlog("dcpu_execute_one: calling i_DEIM()");
        int result = i_DEIM(address);
        vlog("dcpu_execute_one: returning %d", result);
        return result;
    }
    else if (opcode == 004)
    {
        return i_DLVH(address);
    }
    else if (opcode == 005)
    {
        return i_DJMS(address);
    }
    else if (opcode == 006)
    {
        return i_DJMP(address);
    }
    else if (opcode == 007)
    {
        illegal();
    }
    else
    {
        illegal();
    }

    return 0;       // to turn off "control may reach end of non-void function"
}


/******************************************************************************
Description : Function to get CPU state.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
bool
dcpu_running(void)
{
    return Running;
}


/******************************************************************************
Description : Function to start the CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_start(void)
{
    Running = true;
}


/******************************************************************************
Description : Function to stop the CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_stop(void)
{
    Running = false;
}


/******************************************************************************
Description : Function to set the DCPU DRS index.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
dcpu_set_drsindex(int index)
{
    DRSindex = index;
}


/******************************************************************************
Description : Function to get the display X coord.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int
dcpu_get_x(void)
{
    return DX;
}


/******************************************************************************
Description : Function to get the display Y coord.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
int
dcpu_get_y(void)
{
    return DY;
}

