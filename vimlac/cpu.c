/******************************************************************************\
 *                                 cpu.c                                      *
 *                                -------                                     *
 *                                                                            *
 *  This file is used to decode and execute a main processor instruction.     *
 *                                                                            *
\******************************************************************************/

#include "vimlac.h"
#include "cpu.h"
#include "dcpu.h"
#include "memory.h"
#include "kb.h"
#include "ptr.h"
#include "ptp.h"
#include "ttyin.h"
#include "ttyout.h"
#include "trace.h"


/******
 * Emulated registers, state, memory, etc.
 ******/

static WORD            r_AC;
static WORD            r_L;
static WORD            r_PC;
static WORD            Prev_r_PC;
static WORD            r_DS;	/* data switches */

/* 40Hz sync stuff */
static bool            Sync40HzOn = false;

/******
 * Environment stuff.  PTR and TTY in and out files, etc
 ******/

static bool            cpu_on;           /* true if main processor is running */
static bool            cpu_sync_on;      /* true if 40HZ flag set */


/******************************************************************************
Description : Function to start the main CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
cpu_start(void)
{
    cpu_on = true;
}


/******************************************************************************
Description : Function to stop the main CPU.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
void
cpu_stop(void)
{
    cpu_on = false;
}


/******************************************************************************
Description : Functions to get various registers.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
WORD
cpu_get_AC(void)
{
    return r_AC;
}


WORD
cpu_get_L(void)
{
    return r_L;
}


WORD
cpu_get_PC(void)
{
    return r_PC;
}


WORD
cpu_get_prev_PC(void)
{
    return Prev_r_PC;
}


void
cpu_set_PC(WORD new_pc)
{
    r_PC = new_pc;
}


void
cpu_set_DS(WORD new_ds)
{
    r_DS = new_ds;
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
    WORD oldPC = Prev_r_PC & MEMMASK;

/*    memdump(LogOut, oldPC - 8, 16); */

    error("INTERNAL ERROR: "
          "unexpected main processor opcode %06.6o at address %06.6o",
          mem_get(oldPC, false), oldPC);
}


/******************************************************************************
Description : Emulate the IMLAC LAW/LWC instructions.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Load AC with immediate value.
 ******************************************************************************/
static int
i_LAW_LWC(bool indirect, WORD address)
{
    /* here 'indirect' selects between LWC and LAW */
    if (indirect)
    {
        /* LWC */
        r_AC = (~address + 1) & WORD_MASK;
        trace("LWC\t %5.5o", address);
    }
    else
    {
        /* LAW */
        r_AC = address;
        trace("LAW\t %5.5o", address);
    }

    return 1;
}


/******************************************************************************
Description : Emulate the JMP instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : PC set to new address.
 ******************************************************************************/
static int
i_JMP(bool indirect, WORD address)
{
    if (indirect)
        r_PC = mem_get(address, false);
    else
	r_PC = address;

    trace("JMP\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the DAC instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Deposit AC in MEM.
 ******************************************************************************/
static int
i_DAC(bool indirect, WORD address)
{
    mem_put(address, indirect, r_AC);

    trace("DAC\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC XAM instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Exchange AC with MEM.
 ******************************************************************************/
static int
i_XAM(bool indirect, WORD address)
{
    WORD tmp;

    tmp = mem_get(address, indirect);
    mem_put(address, indirect, r_AC);
    r_AC = tmp;

    trace("XAM\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the ISZ instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Increment MEM and skip if MEM == 0.
 ******************************************************************************/
static int
i_ISZ(bool indirect, WORD address)
{
    WORD new_value = (mem_get(address, indirect) + 1) & WORD_MASK;

    mem_put(address, indirect, new_value);
    if (new_value == 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("ISZ\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC JMS instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Store PC in MEM, jump to MEM + 1.
 ******************************************************************************/
static int
i_JMS(bool indirect, WORD address)
{
    WORD new_address = address;

    if (indirect)
	new_address = mem_get(address, indirect);

    mem_put(new_address, false, r_PC);
    r_PC = ++new_address & MEMMASK;

    trace("JMS\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC AND instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : AND MEM with AC.
 ******************************************************************************/
static int
i_AND(bool indirect, WORD address)
{
    r_AC &= mem_get(address, indirect);

    trace("AND\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC IOR instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Inclusive OR MEM with AC.
 ******************************************************************************/
static int
i_IOR(bool indirect, WORD address)
{
    r_AC |= mem_get(address, indirect);

    trace("IOR\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC XOR instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : XOR AC and MEM.  LINK unchanged.
 ******************************************************************************/
static int
i_XOR(bool indirect, WORD address)
{
    r_AC ^= mem_get(address, indirect);

    trace("XOR\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC LAC instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Load AC from MEM.
 ******************************************************************************/
static int
i_LAC(bool indirect, WORD address)
{
    r_AC = mem_get(address, indirect);

    trace("LAC\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the ADD instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Add value at MEM to AC.
 ******************************************************************************/
static int
i_ADD(bool indirect, WORD address)
{
    r_AC += mem_get(address, indirect);
    if (r_AC & OVERFLOWMASK)
    {
        r_L ^= 1;
        r_AC &= WORD_MASK;
    }

    trace("ADD\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC SUB instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Subtract MEM from AC.  LINK complemented if carry.
 ******************************************************************************/
static int
i_SUB(bool indirect, WORD address)
{
    r_AC -= mem_get(address, indirect);
    if (r_AC & OVERFLOWMASK)
    {
        r_L ^= 1;
        r_AC &= WORD_MASK;
    }

    trace("SUB\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}


/******************************************************************************
Description : Emulate the IMLAC SAM instruction.
 Parameters : indirect - TRUE if address is indirect, FALSE if immediate
            : address  - the memory address
    Returns : 
   Comments : Skip if AC same as MEM.
 ******************************************************************************/
static int
i_SAM(bool indirect, WORD address)
{
    if (r_AC == mem_get(address, indirect))
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("SAM\t%c%5.5o", (indirect) ? '*' : ' ', address);

    return (indirect) ? 3 : 2;
}

/******************************************************************************
Description : Decode the 'microcode' instructions.
 Parameters : instruction - the complete instruction word
    Returns : 
   Comments : 
 ******************************************************************************/
static int
microcode(WORD instruction)
{
    char trace_msg[10];		/* little buffer for opcode */

    /* T1 */
    if (instruction & 001)
    {
        r_AC = 0;
    }
    if (instruction & 010)
    {
        r_L = 0;
    }

    /* T2 */
    if (instruction & 002)
    {
        r_AC = (~r_AC) & WORD_MASK;
    }
    if (instruction & 020)
    {
        r_L = (~r_L) & 01;
    }

    /* T3 */
    if (instruction & 004)
    {
        if (++r_AC & OVERFLOWMASK)
            r_L = (~r_L) & 01;
        r_AC &= WORD_MASK;
    }
    if (instruction & 040)
    {
        r_AC |= r_DS;
        r_L = (~r_L) & 1;
    }

    /* do some sort of trace */
    strcpy(trace_msg, "");
    switch (instruction)
    {
        case 0100000: strcat(trace_msg, "NOP"); break;
        case 0100001: strcat(trace_msg, "CLA"); break;
        case 0100002: strcat(trace_msg, "CMA"); break;
        case 0100003: strcat(trace_msg, "STA"); break;
        case 0100004: strcat(trace_msg, "IAC"); break;
        case 0100005: strcat(trace_msg, "COA"); break;
        case 0100006: strcat(trace_msg, "CIA"); break;
        case 0100010: strcat(trace_msg, "CLL"); break;
        case 0100011: strcat(trace_msg, "CAL"); break;
        case 0100020: strcat(trace_msg, "CML"); break;
        case 0100030: strcat(trace_msg, "STL"); break;
        case 0100040: strcat(trace_msg, "ODA"); break;
        case 0100041: strcat(trace_msg, "LDA"); break;
    }

    if ((instruction & 0100000) == 0)
    {
        /* bit 0 is clear, it's HLT */
        cpu_on = false;
	if (trace_msg[0] != 0)
       	    strcat(trace_msg, "+HLT");
	else
       	    strcat(trace_msg, "HLT");
    }

    strcat(trace_msg, "\t");
    trace(trace_msg);

    return 1;
}


/******************************************************************************
Description : Emulate the DSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if display is ON.
 ******************************************************************************/
static int
i_DSF(void)
{
    if (dcpu_on())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("DSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC HRB instruction.
 Parameters : 
    Returns : 
   Comments : Read PTR value into AC.
            : If PTR motor off return 0.
            : If PTR motor on return byte from file.
 ******************************************************************************/
static int
i_HRB(void)
{
    r_AC |= ptr_read();

    trace("HRB\t");

    return 1;
}


/******************************************************************************
Description : Emulate the DSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if display is OFF.
 ******************************************************************************/
static int
i_DSN(void)
{
    if (!dcpu_on())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("DSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC HSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if PTR has data.
   Comments : No data until cycle counter >= 'char ready' number.
 ******************************************************************************/
static int
i_HSF(void)
{
    if (ptr_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("HSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC HSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if PTR has no data.
            : There is no data until cycle counter >= 'char ready' number.
 ******************************************************************************/
static int
i_HSN(void)
{
    if (!ptr_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("HSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC KCF instruction.
 Parameters : 
    Returns : 
   Comments : Clear the keyboard flag.
 ******************************************************************************/
static int
i_KCF(void)
{
    kb_clear_flag();

    trace("KCF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC KRB instruction.
 Parameters : 
    Returns : 
   Comments : Read a character from the keyboard into bits 5-15 of AC.
 ******************************************************************************/
static int
i_KRB(void)
{
    r_AC |= kb_get_char();

    trace("KRB\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC KRC instruction.
 Parameters : 
    Returns : 
   Comments : Combine the KCF and KRB instruction: Read keyboard and clear flag.
 ******************************************************************************/
static int
i_KRC(void)
{
    r_AC |= kb_get_char();
    kb_clear_flag();

    trace("KRC\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC KSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if keyboard char available.
 ******************************************************************************/
static int
i_KSF(void)
{
    if (kb_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("KSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC KSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if no keyboard char available.
 ******************************************************************************/
static int
i_KSN(void)
{
    if (!kb_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("KSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC PUN instruction.
 Parameters : 
    Returns : 
   Comments : Punch AC low byte to tape.
 ******************************************************************************/
static int
i_PUN(void)
{
    ptp_punch(r_AC & 0xff);

    trace("PUN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC PSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if PTP ready.
 ******************************************************************************/
static int
i_PSF(void)
{
    if (ptp_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("PSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RAL instruction.
 Parameters : shift - the number of bits to shift by [1,3]
    Returns : 
   Comments : Rotate AC+L left 'shift' bits.
 ******************************************************************************/
static int
i_RAL(int shift)
{
    for (; shift > 0; --shift)
    {
        WORD oldlink = r_L;

        r_L = (r_AC >> 15) & LOWBITMASK;
        r_AC = ((r_AC << 1) + oldlink) & WORD_MASK;
    }

    trace("RAL\t %d", shift);

    return 1;
}


/******************************************************************************
Description : Emulate the RAR instruction.
 Parameters : shift - number of bits to rotate [1,3]
    Returns : 
   Comments : Rotate right AC+L 'shift' bits.
 ******************************************************************************/
static int
i_RAR(int shift)
{
    for (; shift > 0; --shift)
    {
        WORD oldlink = r_L;

        r_L = r_AC & LOWBITMASK;
        r_AC = ((r_AC >> 1) | (oldlink << 15)) & WORD_MASK;
    }

    trace("RAR\t %d", shift);

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RCF instruction.
 Parameters : 
    Returns : 
   Comments : Clear the TTY buffer flag.
 ******************************************************************************/
static int
i_RCF(void)
{
    ttyin_clear_flag();

    trace("RCF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RRB instruction.
 Parameters : 
    Returns : 
   Comments : Read a character from the TTY into bits 5-15 of AC.
 ******************************************************************************/
static int
i_RRB(void)
{
    r_AC |= ttyin_get_char();

    trace("RRB\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RRC instruction.
 Parameters : 
    Returns : 
   Comments : Read a character from the TTY and clear buffer flag.
 ******************************************************************************/
static int
i_RRC(void)
{
    r_AC |= ttyin_get_char();
    ttyin_clear_flag();

    trace("RRC\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if TTY char available.
 ******************************************************************************/
static int
i_RSF(void)
{
    if (ttyin_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("RSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC RSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if no TTY char available.
 ******************************************************************************/
static int
i_RSN(void)
{
    if (!ttyin_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("RSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC SAL instruction.
 Parameters : shift - the number of bits to shift by
    Returns : 
   Comments : Shift AC left n places.  LINK unchanged.
 ******************************************************************************/
static int
i_SAL(int shift)
{
    WORD oldbit0 = r_AC & HIGHBITMASK;

    while (shift-- > 0)
        r_AC = ((r_AC << 1) & WORD_MASK) | oldbit0;

    trace("SAL\t %d", shift);

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC SAR instruction.
 Parameters : shift - the number of bits to shift by
    Returns : 
   Comments : Shift AC right n places.
 ******************************************************************************/
static int
i_SAR(int shift)
{
    while (shift-- > 0)
    {
        WORD oldbit0 = r_AC & HIGHBITMASK;

        r_AC = (r_AC >> 1) | oldbit0;
    }

    trace("SAR\t %d", shift);

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC SSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if 40Hz sync flip-flop is set.
 ******************************************************************************/
static int
i_SSF(void)
{
    if (cpu_sync_on)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("SSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC SSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if 40Hz sync flip-flop is NOT set.
 ******************************************************************************/
static int
i_SSN(void)
{
    if (!cpu_sync_on)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("SSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC TCF instruction.
 Parameters : 
    Returns : 
   Comments : Reset the TTY "output done" flag.
 ******************************************************************************/
static int
i_TCF(void)
{
    ttyout_clear_flag();

    trace("TCF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC TPC instruction.
 Parameters : 
    Returns : 
   Comments : Transmit char in AC and clear TTY ready flag
 ******************************************************************************/
static int
i_TPC(void)
{
    ttyout_send(r_AC & 0xff);
    ttyout_clear_flag();

    trace("TPC\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC TPR instruction.
 Parameters : 
    Returns : 
   Comments : Send low byte in AC to TTY output.
 ******************************************************************************/
static int
i_TPR(void)
{
    ttyout_send(r_AC & 0xff);

    trace("TPR\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC TSF instruction.
 Parameters : 
    Returns : 
   Comments : Skip if TTY done sending
 ******************************************************************************/
static int
i_TSF(void)
{
    if (ttyout_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("TSF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC TSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if TTY not done sending
 ******************************************************************************/
static int
i_TSN(void)
{
    if (!ttyout_ready())
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("TSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the ASZ instruction.
 Parameters : 
    Returns : 
   Comments : Skip if AC == 0.
 ******************************************************************************/
static int
i_ASZ(void)
{
    if (r_AC == 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("ASZ\t");

    return 1;
}


/******************************************************************************
Description : Emulate the ASN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if AC != 0.
 ******************************************************************************/
static int
i_ASN(void)
{
    if (r_AC != 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("ASN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC ASP instruction.
 Parameters : 
    Returns : 
   Comments : Skip if AC is positive.
 ******************************************************************************/
static int
i_ASP(void)
{
    if ((r_AC & HIGHBITMASK) == 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("ASP\t");

    return 1;
}


/******************************************************************************
Description : Emulate the LSZ instruction.
 Parameters : 
    Returns : 
   Comments : Skip if LINK is zero.
 ******************************************************************************/
static int
i_LSZ(void)
{
    if (r_L == 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("LSZ\t");

    return 1;
}


/******************************************************************************
Description : Emulate the LSN instruction.
 Parameters : 
    Returns : 
   Comments : Skip if LINK isn't zero.
 ******************************************************************************/
static int
i_LSN(void)
{
    if (r_L != 0)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("LSN\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC ASM instruction.
 Parameters : 
    Returns : 
   Comments : Skip if AC is negative.
 ******************************************************************************/
static int
i_ASM(void)
{
    if (r_AC & HIGHBITMASK)
        r_PC = (r_PC + 1) & WORD_MASK;

    trace("ASM\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC DLA instruction.
 Parameters : 
    Returns : 
   Comments : Load display CPU with a new PC.
 ******************************************************************************/
static int
i_DLA(void)
{
    dcpu_set_PC(r_AC);

    trace("DLA\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC CTB instruction.
 Parameters : 
    Returns : 
   Comments : Load display CPU with a new PC.
 ******************************************************************************/
static int
i_CTB(void)
{
    trace("CTB\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC DOF instruction.
 Parameters : 
    Returns : 
   Comments : Turn the display processor off.
 ******************************************************************************/
static int
i_DOF(void)
{
    dcpu_stop();

    trace("DOF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC DON instruction.
 Parameters : 
    Returns : 
   Comments : Turn the display processor on.
 ******************************************************************************/
static int
i_DON(void)
{
    dcpu_set_DRSindex(0);
    dcpu_start();

    trace("DON\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC HOF instruction.
 Parameters : 
    Returns : 
   Comments : Turn the PTR off.
 ******************************************************************************/
static int
i_HOF(void)
{
    ptr_stop();

    trace("HOF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC HON instruction.
 Parameters : 
    Returns : 
   Comments : Turn the PTR on.
 ******************************************************************************/
static int
i_HON(void)
{
    ptr_start();

    trace("HON\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC STB instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_STB(void)
{
    trace("STB\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC SCF instruction.
 Parameters : 
    Returns : 
   Comments : Clear the 40Hz "sync" flag.
 ******************************************************************************/
static int
i_SCF(void)
{
    Sync40HzOn = false;

    trace("SCF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOS instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOS(void)
{
    trace("IOS\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOT101 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT101(void)
{
    trace("IOT101\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOT111 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT111(void)
{
    trace("IOT111\t");

    return 1;
}

/******************************************************************************
Description : Emulate the IMLAC i_IOT131 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT131(void)
{
    trace("i_IOT131\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC i_IOT132 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT132(void)
{
    trace("i_IOT132\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOT134 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT134(void)
{
    trace("IOT134\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOT141 instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOT141(void)
{
    trace("IOT141\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC IOF instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_IOF(void)
{
    trace("IOF\t");

    return 1;
}


/******************************************************************************
Description : Emulate the IMLAC ION instruction.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
static int
i_ION(void)
{
    trace("ION\t");

    return 1;
}


/******************************************************************************
Description : Further decode the initial '02' opcode instruction.
 Parameters : instruction - the complete instruction word
    Returns : 
   Comments : 
 ******************************************************************************/
static int
page02(WORD instruction)
{
    switch (instruction)
    {
        case 0002001: return i_ASZ();
        case 0102001: return i_ASN();
        case 0002002: return i_ASP();
        case 0102002: return i_ASM();
        case 0002004: return i_LSZ();
        case 0102004: return i_LSN();
        case 0002010: return i_DSF();
        case 0102010: return i_DSN();
        case 0002020: return i_KSF();
        case 0102020: return i_KSN();
        case 0002040: return i_RSF();
        case 0102040: return i_RSN();
        case 0002100: return i_TSF();
        case 0102100: return i_TSN();
        case 0002200: return i_SSF();
        case 0102200: return i_SSN();
        case 0002400: return i_HSF();
        case 0102400: return i_HSN();
        default: illegal();
    }
    return 0;	/* CAN'T REACH */
}


/******************************************************************************
Description : Further decode the initial '00' opcode instruction.
 Parameters : instruction - the complete instruction word
    Returns : 
   Comments : 
 ******************************************************************************/
static int
page00(WORD instruction)
{
/******
 * Pick out microcode or page 2 instructions.
 ******/

    if ((instruction & 0077700) == 000000)
        return microcode(instruction);

    if ((instruction & 0077000) == 002000)
        return page02(instruction);

/******
 * Decode a page 00 instruction
 ******/

    switch (instruction)
    {
        case 001003: return i_DLA();
        case 001011: return i_CTB();
        case 001012: return i_DOF();
        case 001021: return i_KRB();
        case 001022: return i_KCF();
        case 001023: return i_KRC();
        case 001031: return i_RRB();
        case 001032: return i_RCF();
        case 001033: return i_RRC();
        case 001041: return i_TPR();
        case 001042: return i_TCF();
        case 001043: return i_TPC();
        case 001051: return i_HRB();
        case 001052: return i_HOF();
        case 001061: return i_HON();
        case 001062: return i_STB();
        case 001071: return i_SCF();
        case 001072: return i_IOS();
        case 001101: return i_IOT101();
        case 001111: return i_IOT111();
        case 001131: return i_IOT131();
        case 001132: return i_IOT132();
        case 001134: return i_IOT134();
        case 001141: return i_IOT141();
        case 001161: return i_IOF();
        case 001162: return i_ION();
        case 001271: return i_PUN();
        case 001274: return i_PSF();
        case 003001: return i_RAL(1);
        case 003002: return i_RAL(2);
        case 003003: return i_RAL(3);
        case 003021: return i_RAR(1);
        case 003022: return i_RAR(2);
        case 003023: return i_RAR(3);
        case 003041: return i_SAL(1);
        case 003042: return i_SAL(2);
        case 003043: return i_SAL(3);
        case 003061: return i_SAR(1);
        case 003062: return i_SAR(2);
        case 003063: return i_SAR(3);
        case 003100: return i_DON();
	default: illegal();
    }

    return 0;	/* CAN'T REACH */
}


/******************************************************************************
Description : Function to execute one main processor instruction.
 Parameters : 
    Returns : 
   Comments : Perform initial decode of 5 bit opcode and either call
            : appropriate emulating function or call further decode function.
 ******************************************************************************/
int
cpu_execute_one(void)
{
    WORD instruction;
    bool indirect;
    WORD opcode;
    WORD address;

/******
 * If main processor not running, return immediately.
 ******/

    if (!cpu_on)
        return 0;

/******
 * If interrupt pending, force JMS 0.
 ******/

#ifdef JUNK
    if (InterruptsEnabled && (InterruptWait <= 0) && InterruptsPending)
    {
        InterruptsEnabled = false;
        i_JMS(false, 0);
        return 0;
    }
#endif

/******
 * Fetch the instruction.  Split into initial opcode and address.
 ******/

    Prev_r_PC = r_PC;
    instruction = mem_get(r_PC++, false);
    r_PC = r_PC & MEMMASK;

    indirect = (bool) (instruction & 0100000);	/* high bit set? */
    opcode = (instruction >> 11) & 017;		/* high 5 bits */
    address = instruction & 03777;		/* low 11 bits */

/******
 * Now decode it.
 ******/

    switch (opcode)
    {
        case 000: return page00(instruction);
        case 001: return i_LAW_LWC(indirect, address);
        case 002: return i_JMP(indirect, address);
        /* case 003: illegal(); */
        case 004: return i_DAC(indirect, address);
        case 005: return i_XAM(indirect, address);
        case 006: return i_ISZ(indirect, address);
        case 007: return i_JMS(indirect, address);
        /* case 010: illegal(); */
        case 011: return i_AND(indirect, address);
        case 012: return i_IOR(indirect, address);
        case 013: return i_XOR(indirect, address);
        case 014: return i_LAC(indirect, address);
        case 015: return i_ADD(indirect, address);
        case 016: return i_SUB(indirect, address);
        case 017: return i_SAM(indirect, address);
	default: illegal();
    }

    return 0;	/* CAN'T REACH */
}


