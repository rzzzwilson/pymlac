/******************************************************************************\
 *                                assemble.c                                  *
 *                               ------------                                 *
 *                                                                            *
 *  The actual assembler implementation.                                      *
 *                                                                            *
 *  The assembler is a two-pass assembler.  The first pass just fills the     *
 *  symbol table with addresses.  The second pass does most of the work.      *
 *                                                                            *
\******************************************************************************/

#include "iasm.h"
#include "assemble.h"


/******
 * Local constants, definitions, etc.
 ******/

#define BUFFERSIZE		1024
#define MAXNAME_LEN             7
#define HASHTABSIZE             1023
#define MAXBLOCKSIZE            255
#define WORDADDRMASK            03777
#define INDIRECTBIT             (1 << 15)
#define WORDMASK                0xFFFF

typedef int WORD;

typedef struct sym		/* one symbol */
{
    struct sym *next;			/* next symbol */
    char       name[MAXNAME_LEN + 1];	/* symbol name */
    WORD       address;			/* symbol address */
} SYM;


/******
 * File globals.
 ******/

static char inputline[BUFFERSIZE + 1];
static SYM  *hashtab[HASHTABSIZE];

static long dot = -1L;
static WORD codeblockstart = 0;
static WORD codeblock[MAXBLOCKSIZE];
static int  nextcodeword = 0;

static int  LineNumber = 0;


typedef enum
{
    AYES,		/* address MUST be supplied */
    ANO,		/* address must NOT be supplied */
    AOPT		/* address field is optional */
} ADDROPT;

typedef struct
{
    char    *opcode;		/* opcode string */
    WORD    code;		/* WORD of code for opcode */
    ADDROPT address;		/* address allowed  options */
    WORD    addrmask;		/* bitmask for address */
    BOOL    indirect;		/* TRUE if indirect allowed */
} OPCODE;

OPCODE opcodes[] =
{
    { "LAW",  0004000, AYES, 03777, FALSE },
    { "LWC",  0104000, AYES, 03777, FALSE },
    { "JMP",  0010000, AYES, 03777, TRUE  },
    { "DAC",  0020000, AYES, 03777, TRUE  },
    { "XAM",  0024000, AYES, 03777, TRUE  },
    { "ISZ",  0030000, AYES, 03777, TRUE  },
    { "JMS",  0034000, AYES, 03777, TRUE  },
    { "AND",  0044000, AYES, 03777, TRUE  },
    { "IOR",  0050000, AYES, 03777, TRUE  },
    { "XOR",  0054000, AYES, 03777, TRUE  },
    { "LAC",  0060000, AYES, 03777, TRUE  },
    { "ADD",  0064000, AYES, 03777, TRUE  },
    { "SUB",  0070000, AYES, 03777, TRUE  },
    { "SAM",  0074000, AYES, 03777, TRUE  },

    { "HLT",  0000000, AOPT, 03777, FALSE },
    { "NOP",  0100000, ANO,  0,     FALSE },
    { "CLA",  0100001, ANO,  0,     FALSE },
    { "CMA",  0100002, ANO,  0,     FALSE },
    { "STA",  0100003, ANO,  0,     FALSE },
    { "IAC",  0100004, ANO,  0,     FALSE },
    { "COA",  0100005, ANO,  0,     FALSE },
    { "CIA",  0100006, ANO,  0,     FALSE },
    { "CLL",  0100010, ANO,  0,     FALSE },
    { "CML",  0100020, ANO,  0,     FALSE },
    { "STL",  0100030, ANO,  0,     FALSE },
    { "ODA",  0100040, ANO,  0,     FALSE },
    { "LDA",  0100041, ANO,  0,     FALSE },
    { "CAL",  0100011, ANO,  0,     FALSE },

    { "RAL",  0003000, AYES, 03,    FALSE },
    { "RAR",  0003020, AYES, 03,    FALSE },
    { "SAL",  0003040, AYES, 03,    FALSE },
    { "SAR",  0003060, AYES, 03,    FALSE },
    { "DON",  0003100, ANO,  0,     FALSE },

    { "ASZ",  0002001, ANO,  0,     FALSE },
    { "ASN",  0102001, ANO,  0,     FALSE },
    { "ASP",  0002002, ANO,  0,     FALSE },
    { "ASM",  0102002, ANO,  0,     FALSE },
    { "LSZ",  0002004, ANO,  0,     FALSE },
    { "LSN",  0102004, ANO,  0,     FALSE },
    { "DSF",  0002010, ANO,  0,     FALSE },
    { "DSN",  0102010, ANO,  0,     FALSE },
    { "KSF",  0002020, ANO,  0,     FALSE },
    { "KSN",  0102020, ANO,  0,     FALSE },
    { "RSF",  0002040, ANO,  0,     FALSE },
    { "RSN",  0102040, ANO,  0,     FALSE },
    { "TSF",  0002100, ANO,  0,     FALSE },
    { "TSN",  0102100, ANO,  0,     FALSE },
    { "SSF",  0002200, ANO,  0,     FALSE },
    { "SSN",  0102200, ANO,  0,     FALSE },
    { "HSF",  0002400, ANO,  0,     FALSE },
    { "HSN",  0102400, ANO,  0,     FALSE },

    { "DLA",  0001003, ANO,  0,     FALSE },
    { "CTB",  0001011, ANO,  0,     FALSE },
    { "DOF",  0001012, ANO,  0,     FALSE },
    { "KRB",  0001021, ANO,  0,     FALSE },
    { "KCF",  0001022, ANO,  0,     FALSE },
    { "KRC",  0001023, ANO,  0,     FALSE },
    { "RRB",  0001031, ANO,  0,     FALSE },
    { "RCF",  0001032, ANO,  0,     FALSE },
    { "RRC",  0001033, ANO,  0,     FALSE },
    { "TPR",  0001041, ANO,  0,     FALSE },
    { "TCF",  0001042, ANO,  0,     FALSE },
    { "TPC",  0001043, ANO,  0,     FALSE },
    { "HRB",  0001051, ANO,  0,     FALSE },
    { "HOF",  0001052, ANO,  0,     FALSE },
    { "HON",  0001061, ANO,  0,     FALSE },
    { "STB",  0001062, ANO,  0,     FALSE },
    { "SCF",  0001071, ANO,  0,     FALSE },
    { "IOS",  0001072, ANO,  0,     FALSE },

    { "IOT",  0001000, AYES, 0777,  FALSE },
    { "IOF",  0001161, ANO,  0,     FALSE },
    { "ION",  0001162, ANO,  0,     FALSE },
    { "PUN",  0001171, ANO,  0,     FALSE },
    { "PSF",  0001174, ANO,  0,     FALSE },
    { "PPC",  0001271, ANO,  0,     FALSE },

    { "DLXA", 0010000, AYES, 07777, FALSE },
    { "DLYA", 0020000, AYES, 07777, FALSE },
/*     { "DEIM", 0030000, AYES, 07777, FALSE }, handled as pseudo-op */
    { "DJMS", 0050000, AYES, 07777, FALSE },
    { "DJMP", 0060000, AYES, 07777, FALSE },

    { "DOPR", 0004000, AYES, 017,   FALSE },
    { "DHLT", 0000000, ANO,  0,     FALSE },
    { "DSTS", 0004004, AYES, 03,    FALSE },
    { "DSTB", 0004010, AYES, 07,    FALSE },
    { "DRJM", 0004040, ANO,  0,     FALSE },
    { "DIXM", 0005000, ANO,  0,     FALSE },
    { "DIYM", 0004400, ANO,  0,     FALSE },
    { "DDXM", 0004200, ANO,  0,     FALSE },
    { "DDYM", 0004100, ANO,  0,     FALSE },
    { "DHVC", 0006000, ANO,  0,     FALSE },
    { "DDSP", 0004020, ANO,  0,     FALSE },
    { "DNOP", 0004000, ANO,  0,     FALSE },
};

#define NUMOPCODES                      (sizeof(opcodes) / sizeof(opcodes[0]))


/******
 * The PTR block loader, origin at 03700.
 ******/

#define ZEROLEADERSIZE                  2

WORD blkldr[] =
{
             /* ; Imlac Papertape Program Block Loader                                          */
             /* ;                                                                               */
             /* ; This loader is loaded by the bootstrap program at x7700, where x=0 for        */
             /* ; a 4K machine, and x=1 for an 8K machine, etc.                                 */
             /* ;                                                                               */
             /* ; The load format consists of one or more contiguous blocks, with no            */
             /* ; padding bytes between them.  Each block has the form:                         */
             /* ;                                                                               */
             /* ;          word count      (byte)                                               */
             /* ;          load address                                                         */
             /* ;          data word 1                                                          */
             /* ;          data word 2                                                          */
             /* ;          ...                                                                  */
             /* ;          data word n                                                          */
             /* ;          checksum                                                             */
             /* ;                                                                               */
             /* ; All values are 16bit words, except the word count, which is an 8bit byte.     */
             /* ; Words are always received high-order byte first.                              */
             /* ;                                                                               */
             /* ; After the word count there is the load address, followed by <word count>      */
             /* ; data words, which are loaded starting at "load address".                      */
             /* ;                                                                               */
             /* ; The sum of all the data words in the block must be the same as the checksum   */
             /* ; word which follows the data words.  The checksum is calculated with 16bit     */
             /* ; integers, incrementing the sum whenever the 16bit value overflows.            */
             /* ;                                                                               */
             /* ; The end of the load is signalled by a block with a negative starting address. */
             /* ;                                                                               */
             /* ; Disassembled from the 40tp_simpleDisplay.ptp image file.                      */
             /* ;                                                                               */
             /*			org	003700	;		                        	*/
             /*		cksum	equ	.-1	;checksum stored here (before loader)		*/
    0001032, /* 003700		rcf		;		                        	*/
    0013740, /* 003701		jmp	patch	;go decide TTY or PTR, clear AC        	        */
    0023677, /* 003702	ndpatch	dac	cksum	;zero checksum, AC is zero (from patch)		*/
    0037760, /* 003703		jms	rdbyte	;		                        	*/
    0102001, /* 003704		asn		;wait here for non-zero byte			*/
    0013703, /* 003705		jmp	.-2	;		                        	*/
    0100006, /* 003706		cia		;		                        	*/
    0023777, /* 003707		dac	wrdcnt	;store negative word count			*/
    0037750, /* 003710		jms	rdword	;read load address		        	*/
    0023776, /* 003711		dac	ldaddr	;		                        	*/
    0077730, /* 003712		sam	neg1	;		                        	*/
    0013715, /* 003713		jmp	rdblock	;		                        	*/
    0000000, /* 003714		hlt		;if load address is -1, halt - finished		*/
    0037750, /* 003715	rdblock	jms	rdword	;now read block to load address			*/
    0123776, /* 003716		dac	*ldaddr	;		                        	*/
    0037731, /* 003717		jms	dosum	;		                        	*/
    0033776, /* 003720		isz	ldaddr	;		                        	*/
    0033777, /* 003721		isz	wrdcnt	;		                        	*/
    0013715, /* 003722		jmp	rdblock	;		                        	*/
    0037750, /* 003723		jms	rdword	;get expected checksum		        	*/
    0073677, /* 003724		sub	cksum	;compare with calculated			*/
    0102001, /* 003725		asn		;		                        	*/
    0013746, /* 003726		jmp	newblk	;if same, get next block			*/
    0000000, /* 003727		hlt		;if not same, ERROR		        	*/
    0177777, /* 003730	neg1	data	0177777	;		                        	*/
             /* 		;------------------------		                        */
             /* 		;Compute checksum.  Word to sum in AC.		                */
             /* 		;------------------------		                        */
    0017720, /* 003731	dosum	bss	1	;		                        	*/
    0100010, /* 003732		cll		;		                        	*/
    0067677, /* 003733		add	cksum	;		                        	*/
    0002004, /* 003734		lsz		;		                        	*/
    0100004, /* 003735		iac		;		                        	*/
    0023677, /* 003736		dac	cksum	;		                        	*/
    0113731, /* 003737		jmp	*dosum	;		                        	*/
             /* 		;------------------------		                        */
             /* 		;Decide what input device we are using, PTR or TTY.		*/
             /* 		;------------------------		                        */
    0001061, /* 003740	patch	hon		;		                        	*/
    0063774, /* 003741		lac	ttyset	;		                        	*/
    0023761, /* 003742		dac	devpat	;		                        	*/
    0005032, /* 003743		law	1032	;		                        	*/
    0177775, /* 003744		sam	*adr044	;		                        	*/
    0023761, /* 003745		dac	devpat	;		                        	*/
    0100011, /* 003746	newblk	cal		;		                        	*/
    0013702, /* 003747		jmp	ndpatch	;		                        	*/
             /* 		;------------------------		                        */
             /* 		;Read WORD from input device.		                        */
             /* 		;------------------------		                        */
    0017711, /* 003750	rdword	bss	1	;		                        	*/
    0100011, /* 003751		cal		;		                        	*/
    0037760, /* 003752		jms	rdbyte	;		                        	*/
    0003003, /* 003753		ral	3	;		                        	*/
    0003003, /* 003754		ral	3	;		                        	*/
    0003002, /* 003755		ral	2	;		                        	*/
    0037760, /* 003756		jms	rdbyte	;		                        	*/
    0113750, /* 003757		jmp	*rdword	;		                        	*/
             /* 		;------------------------		                        */
             /* 		;Read BYTE from input device. Read from PTR or TTY.		*/
             /* 		;------------------------		                        */
    0017757, /* 003760	rdbyte	bss	1	;		                        	*/
    0001032, /* 003761	devpat	rcf		;could be patched to 'jmp rdtty'		*/
    0102400, /* 003762		hsn		;		                        	*/
    0013762, /* 003763		jmp	.-1	;		                        	*/
    0002400, /* 003764		hsf		;		                        	*/
    0013764, /* 003765		jmp	.-1	;		                        	*/
    0001051, /* 003766		hrb		;read PTR byte		                	*/
    0113760, /* 003767		jmp	*rdbyte	;		                        	*/
    0002040, /* 003770	rdtty	rsf		;		                        	*/
    0013770, /* 003771		jmp	.-1	;		                        	*/
    0001033, /* 003772		rrc		;read TTY byte, clear flag			*/
    0113760, /* 003773		jmp	*rdbyte	;		                        	*/
             /* 		;------------------------		                        */
    0013770, /* 003774	ttyset	jmp	rdtty	;		                        	*/
    0000044, /* 003775	adr044	data	044	;		                        	*/
    0000000, /* 003776	ldaddr	data	0	;		                        	*/
    0000000  /* 003777	wrdcnt	data	0	;		                        	*/
             /* 		;------------------------		                        */
             /* 			end		;		                        */
};

#define BLKLDR_SIZE          (sizeof(blkldr)/sizeof(blkldr[0]))


/******
 * Forward prototypes.
 ******/

static WORD   atoo(char *str);
static SYM    *deflabel(char *name, WORD address);
static void   emitblock(void);
static void   emitbyte(WORD word);
static void   emitloader(void);
static void   emitstart();
static void   emitword(WORD word);
static void   emitcode(WORD code);
static WORD   geninc(char *field);
static WORD   genincbyte(char *field);
static void   genlist(WORD code);
static WORD   getaddress(char *field, BOOL indok);
static int    hash(char *name);
static BOOL   isdecimal(char *str);
static BOOL   islabel(char *name);
static BOOL   isoctal(char *str);
static SYM    *lookup(char *label);
static OPCODE *lookupopcode(char *opcode);
static void   newcodeblock(WORD org);
static SYM    *newSYM(char *name);
static void   strupper(char *str);
static void   synerror(char *buff, char *fmt, ...);


/******************************************************************************
       Name : atoo()
Description : Get octal number from a string.
 Parameters : str - string to get octal number from
    Returns : The octal value of the string.
   Comments : 
 ******************************************************************************/
static WORD
atoo(char *str)
{
    WORD result = 0;

    for (; *str; ++str)
        result = result * 8 + *str - '0';

    return result;
}


/******************************************************************************
       Name : deflabel()
Description : Define a label in the symbol table.
 Parameters : name - name to define
            : addr - the label address
    Returns : 
   Comments : 
 ******************************************************************************/
static SYM *
deflabel(char *name, WORD addr)
{
    int hashval = hash(name);
    SYM *newsym = newSYM(name);

    newsym->address = addr;

    newsym->next = hashtab[hashval];
    hashtab[hashval] = newsym;

    return newsym;
}


/******************************************************************************
       Name : delimfields()
Description : Delimit label, opcode and address fields of assembler line.
 Parameters : buffer  - address of line buffer
            : label   - address of label pointer (returned)
            : opcode  - address of opcode pointer (returned)
            : field   - address of address field pointer (returned)
            : comment - address of comment string (returned)
    Returns : 
   Comments : The buffer is broken into shorter strings (destroyed).
 ******************************************************************************/
static void
delimfields(char *buffer,
            char **label, char **opcode, char **field, char **comment)
{
    char *chptr;

    /* point 'label', 'opcode' and 'field' to strings */
    *label = *opcode = *field = *comment = NULL;

    chptr = buffer;
    if (isalpha(*chptr))
    {
        *label = chptr;
        while (!isspace(*chptr) && *chptr != ';' && *chptr != '\n')
            ++chptr;
        *chptr = '\0';
        ++chptr;
    }

    while (isspace(*chptr) && *chptr != ';' && *chptr != '\n')
        ++chptr;
    if (*chptr != ';' && *chptr != '\n')
    {
        *opcode = chptr;
        while (!isspace(*chptr))
            ++chptr;
        *chptr = '\0';
        ++chptr;

        while (isspace(*chptr) && *chptr != ';' && *chptr != '\n')
            ++chptr;
        if (*chptr != ';' && *chptr != '\n')
        {
            *field = chptr;
            while (!isspace(*chptr) && *chptr != ';' && *chptr != '\n')
                ++chptr;
            *chptr = '\0';
            if (strlen(*field) == 0)
                *field = NULL;
        }
    }

    if (*chptr == ';')
        *comment = chptr;

    if (*label)
        strupper(*label);
    if (*opcode)
        strupper(*opcode);
    if (*field)
        strupper(*field);
}


/******************************************************************************
       Name : emitblock()
Description : Emit the code for the current block.
 Parameters : 
    Returns : 
   Comments : 
 *****************************************************************************/
static void
emitblock(void)
{
    if (nextcodeword > 0)
    {
        WORD checksum;
        int  i;

    /******
     * Emit block header stuff.
     ******/

        emitbyte(nextcodeword);
        emitword(codeblockstart);

    /******
     * Calculate the checksum while we emit code.
     ******/

        checksum = 0;

        for (i = 0; i < nextcodeword; ++i)
        {
            checksum = checksum + codeblock[i];
            if (checksum & ~WORDMASK)
                ++checksum;
            checksum &= WORDMASK;
            emitword(codeblock[i]);
        }

    /******
     * Emit bchecksum.
     ******/

        emitword(checksum);
    }
}


/******************************************************************************
       Name : emitbyte()
Description : Emit one BYTE to output stream.
 Parameters : word - the BYTE value to emit
    Returns : 
   Comments : 
 ******************************************************************************/
static void
emitbyte(WORD word)
{
    fputc(word & 0xFF, OutFile);
}


/******************************************************************************
       Name : emitcode()
Description : Generate code for one word.
 Parameters : code - the WORD to put into current code block
    Returns : 
   Comments : If the block buffer is full, spill to the output file first.
 ******************************************************************************/
static void
emitcode(WORD code)
{
    if (dot == -1L)
        synerror(inputline, "Expected ORG pseudo-op");

    /* if current block is full, emit and reset */
    if (nextcodeword >= MAXBLOCKSIZE)
    {
        emitblock();

        codeblockstart = dot;
        nextcodeword = 0;
    }

    codeblock[nextcodeword++] = code;
}


/******************************************************************************
       Name : emitloader()
Description : Emit papertape loader.
 Parameters : fname - output filename (for error reporting)
    Returns : 
   Comments : 
 ******************************************************************************/
static void
emitloader(void)
{
    int i;

    for (i = 0; i < ZEROLEADERSIZE; ++i)
        emitbyte(0);

    for (i = 0; i < BLKLDR_SIZE; ++i)
        emitword(blkldr[i]);

    for (i = 0; i < ZEROLEADERSIZE; ++i)
        emitbyte(0);
}


/******************************************************************************
       Name : emitstart()
Description : Emit papertape end-of-code start block.
 Parameters : address - the program start address
    Returns : 
   Comments : We have to emit a block size byte, just use 1
 ******************************************************************************/
static void
emitstart(WORD address)
{
    emitbyte(1);		/* one byte block */
    emitword(address);		/* start address */
}


/******************************************************************************
       Name : emitword()
Description : Emit one WORD to output stream.
 Parameters : word - the WORD value to emit
            : out  - open FILE stream for output
    Returns : 
   Comments : 
 ******************************************************************************/
static void
emitword(WORD word)
{
    fputc((word >> 8) & 0xFF, OutFile);
    fputc(word & 0xFF, OutFile);
}


/******************************************************************************
       Name : gencode()
Description : Generate code for one line.
 Parameters : olabel  - pointer to label token (NULL if no label)
            : oopcode - pointer to opcode token (NULL if no opcode)
            : ofield  - pointer to field buffer (NULL if no field)
            : comment - pointer to coment buffer (NULL if no field)
    Returns : TRUE if assembly should continue, FALSE if END opcode found.
   Comments : Called by pass 2.
 ******************************************************************************/
static BOOL
gencode(char *olabel, char *oopcode, char *ofield, char *comment)
{
    BOOL result = TRUE;
    char *label = CopyStr(olabel);
    char *opcode = CopyStr(oopcode);
    char *field = CopyStr(ofield);

/******
 * If there is a label, make sure it's valid.
 ******/

    if (label != NULL && !islabel(label))
        synerror(inputline, "Label '%s' is not legal", olabel);

/******
 * If there is an opcode, handle it.
 ******/

    if (opcode != NULL)
    {
        if (STREQ(opcode, "ORG"))
        {
            if (label != NULL)
                synerror(inputline, "Label not allowed on ORG statement");

            if (field == NULL || !isoctal(field))
                synerror(inputline, "ORG statement must have octal address");

            emitblock();
            dot = atoo(field);
            newcodeblock(dot);
            genlist(-1);
        }
        else if (STREQ(opcode, "END"))
        {
            if (label != NULL)
                synerror(inputline, "Label not allowed on END statement"); 
            if (field != NULL)
                synerror(inputline, "Address not allowed on END statement"); 
            result = FALSE;
            genlist(-1);
        }
        else if (STREQ(opcode, "DATA"))
        {
            WORD   code;

            if (field == NULL)
                synerror(inputline, "Data field required on DATA statement"); 
            if (isoctal(field))
                code = atoo(field);
            else if (isdecimal(field))
                code = atoi(field);
            else
                code = getaddress(field, FALSE);
/*                 synerror(inputline, "DATA field must be octal or decimal");  */

            emitcode(code);
            genlist(code);
            ++dot;
        }
        else if (STREQ(opcode, "INC"))
        {
            WORD code = geninc(field);

            emitcode(code);
            genlist(code);
            ++dot;
        }
        else
        {
            OPCODE *optr = lookupopcode(opcode);
            WORD   code;

            if (optr == NULL)
                synerror(inputline, "Unrecognised opcode");

            if (optr->address == AYES && field == NULL)
                synerror(inputline, "Opcode requires address field");

            if (optr->address == ANO && field != NULL)
                synerror(inputline, "Opcode must not have address field");

            code = optr->code;

            if (field != NULL)
            {
                WORD address;
                WORD mask = optr->addrmask;

                if (optr->indirect)
                    mask |= INDIRECTBIT;

                address = getaddress(field, optr->indirect);
                if (address & ~mask)
                    synerror(inputline, "Address field overflow!");

                code = (code & ~optr->addrmask) | address;
            }

            emitcode(code);
            genlist(code);
            ++dot;
        }
    }
    else	/* blank line */
        genlist(-1);

/******
 * Return line assemble result.
 ******/

    return result;
}


/******************************************************************************
       Name : geninc()
Description : Generate code for one word of INC code.
 Parameters : field  - INC field to generate code for
    Returns : The code word generated.
   Comments : 
 ******************************************************************************/
static WORD
geninc(char *field)
{
    char *endfld;
    WORD highbyte;
    WORD lowbyte;

    if (field == NULL)
        synerror(inputline, "Data field required on INC statement"); 

    endfld = strchr(field, ',');
    if (endfld == NULL)
        synerror(inputline, "Bad data field on INC statement");
    *endfld = '\0';
    ++endfld;

    highbyte = genincbyte(field);
    lowbyte = genincbyte(endfld);

    return (highbyte << 8) | lowbyte;
}

            
/******************************************************************************
       Name : genincbyte()
Description : Generate code for one byte of INC code.
 Parameters : infile - input filename (error reporting)
            : lnum   - input line number (error reporting)
            : field  - INC byte field to generate code for
    Returns : 
   Comments : 
 ******************************************************************************/
static WORD
genincbyte(char *field)
{
    static int  beam = 1;

    int  x;
    int  y;
    int  xneg = 0;
    int  yneg = 0;

    switch (toupper(*field))
    {
        case 'A':	/* make byte */
            ++field;
            if (isoctal(field))
                return atoo(field);
            else if (isdecimal(field))
                return atoi(field);
            else
                synerror(inputline, "Bad INC 'A' field");
            break;
        case 'B':		/* beam on */
            beam = 1;
            ++field;
            break;
        case 'D':		/* beam off */
            beam = 0;
            ++field;
            break;
        case 'E':		/* enter INC mode */
/*            beam = 1; UNUSED */
            return 0060;
            break;
        case 'F':		/* escape INC mode */
            return 0171;
            break;
        case 'N':
            return 0111;
            break;
        case 'P':		/* pause (filler) */
            return 0200;
            break;
        case 'R':
            return 0151;
            break;
        case 'X':
            return 0010;
            break;
        case 'Y':
            return 0001;
            break;
        case '+': case '-': case '0': case '1': case '2': case '3':
            break;
        default:
            synerror(inputline, "Bad INC field");
            break;
    }

    if (*field == '+')
    {
        xneg = 0;
        ++field;
    }
    else if (*field == '-')
    {
        xneg = 1;
        ++field;
    }

    if (strchr("0123", *field) == NULL)
        synerror(inputline, "Bad INC field");

    x = *field - '0';
    ++field;

    if (*field == '+')
    {
        yneg = 0;
        ++field;
    }
    else if (*field == '-')
    {
        yneg = 1;
        ++field;
    }

    if (strchr("0123", *field) == NULL)
        synerror(inputline, "Bad INC field");

    y = *field - '0';
    ++field;

    if (strlen(field) != 0)
        synerror(inputline, "Bad INC field");

    return 0200 | (beam << 6) | (xneg << 5) | (x << 3) | (yneg << 2) | y;
}

            

/******************************************************************************
       Name : genlist()
Description : Generate a listing line, if required.
 Parameters : code  - the code word generated by this instruction
    Returns : 
   Comments : If 'code' is -1, don't show code word.
 ******************************************************************************/
static void
genlist(WORD code)
{
    if (ListFile != NULL)
    {
        if (code == -1)
            fprintf(ListFile, "                 %4d:\t%s",
                    LineNumber, inputline);
        else
            fprintf(ListFile, "%6.6o   %6.6o  %4d:\t%s",
                    code, (int) dot, LineNumber, inputline);
    }
}


/******************************************************************************
       Name : getaddress()
Description : Get an address value from the 'field' string.
 Parameters : field  - the field string to get the address from
            : indok  - TRUE if indirection allowed
    Returns : The address value.
   Comments : A valid address field can be:
            :    <label>
            :    <octal>
            :    .+<octal>
            :    .-<octal>
            : If the field is a <label> and the label is not yet defined, create
            : a fixup and return a zero address.
 ******************************************************************************/
static WORD
getaddress(char *field, BOOL indok)
{
    WORD result = 0;
    SYM  *sym;

/******
 * If indirect flag, note and continue.
 ******/

    if (*field == '*')
    {
        result = INDIRECTBIT;
        ++field;
    }

    switch (*field)
    {
        case '0':		/* an octal value */
            if (!isoctal(field))
                synerror(inputline, "Bad octal address");
            result |= atoo(field);
            break;
        case '1': case '2': case '3': case '4': case '5':
        case '6': case '7': case '8': case '9':		/* a decimal value */
            if (!isdecimal(field))
                synerror(inputline, "Bad decimal address");
            result |= atoi(field);
            break;
        case '.':		/* a relative value */
            ++field;
            if (!isoctal(field + 1) && !isdecimal(field + 1))
                synerror(inputline, "Badly formed address");
            switch (*field)
            {
                case '+':
                    if (isoctal(field + 1))
                        result |= dot + atoo(field + 1);
                    else
                        result |= dot + atoi(field + 1);
                    break;
                case '-':
                    if (isoctal(field + 1))
                        result |= dot - atoo(field + 1);
                    else
                        result |= dot - atoi(field + 1);
                    break;
                default:
                    synerror(inputline, "Badly formed address");
            }
            break;
        default:		/* probably a label */
            if (!islabel(field))
                synerror(inputline, "Illegal address");
            sym = lookup(field);
            if (sym == NULL)
                synerror(inputline, "Badly formed address");
            result |= sym->address;
            break;
    }

    return result;
}


/******************************************************************************
       Name : hash()
Description : Generate a hash value for a name.
 Parameters : name - name string to make hash value for
    Returns : The hash value in range [0,HASHTABSIZE).
   Comments : 
 ******************************************************************************/
static int
hash(char *name)
{
    int result = *name * strlen(name);

    while (*++name)
        result = (result << 1) + *name;

    return result / HASHTABSIZE;
}


/******************************************************************************
       Name : isdecimal()
Description : Function to decide if a string is purely a decimal number.
 Parameters : str - string to look at
    Returns : TRUE if 'str' is a decimal number, else FALSE.
   Comments : 
 ******************************************************************************/
static BOOL
isdecimal(char *str)
{
    for (; *str; ++str)
        if (*str < '0' || *str > '9')
            return FALSE;

    return TRUE;
}


/******************************************************************************
       Name : islabel()
Description : Function to decide if a string is a legal label.
 Parameters : name - string to check
    Returns : TRUE if 'name' is legal label string, else FALSE.
   Comments : 
 ******************************************************************************/
static BOOL
islabel(char *name)
{
    if (!isalpha(*name))
        return FALSE;

    for (; *name; ++name)
        if (!isalpha(*name) && !isdigit(*name))
            return FALSE;

    return TRUE;
}


/******************************************************************************
       Name : isoctal()
Description : Function to decide if a string is purely an octal number.
 Parameters : str - string to look at
    Returns : TRUE if 'str' is an octal number, else FALSE.
   Comments : An octal number must start with a '0' and contain only octal
            : digits after that,
 ******************************************************************************/
static BOOL
isoctal(char *str)
{
    if (*str != '0')
        return FALSE;

    for (; *str; ++str)
        if (*str < '0' || *str > '7')
            return FALSE;

    return TRUE;
}


/******************************************************************************
       Name : lookup()
Description : Lookup a name in the symbol table.
 Parameters : name - name string to look for
    Returns : Address of SYM for name 'name' if found, else NULL.
   Comments : 
 ******************************************************************************/
static SYM *
lookup(char *name)
{
    char *uname = CopyStr(name);
    SYM  *result;

    strupper(uname);
    result = hashtab[hash(uname)];

    while (result != NULL)
    {
        if (STREQ(result->name, name))
            return result;

        result = result->next;
    }

    return NULL;
}


/******************************************************************************
       Name : lookupopcode()
Description : Lookup an opcode in opcodes[] table.
 Parameters : opcode - opcode to lookup
    Returns : Address of OPCODE struct if found, else NULL.
   Comments : 
 ******************************************************************************/
static OPCODE *
lookupopcode(char *opcode)
{
    int    i;

    for (i = 0; i < NUMOPCODES; ++i)
        if (STREQ(opcodes[i].opcode, opcode))
            return &opcodes[i];

    return NULL;
}


/******************************************************************************
       Name : newcodeblock()
Description : Prepare for a new block of code.
 Parameters : org - start address of block
    Returns : 
   Comments : 
 ******************************************************************************/
static void
newcodeblock(WORD org)
{
    codeblockstart = org;
    nextcodeword = 0;
}


/******************************************************************************
       Name : newSYM()
Description : Create a new SYM object.
 Parameters : name - name string of new symbol
    Returns : Address of new SYM object.
   Comments : 
 ******************************************************************************/
static SYM *
newSYM(char *name)
{
    SYM *result = malloc(sizeof(SYM));

    if (result == NULL)
        Error("Out of memory in file '%s', line %d", __FILE__, __LINE__);

    result->next = NULL;
    strcpy(result->name, name);
    result->address = 0;

    return result;
}


/******************************************************************************
       Name : numgenwords()
Description : Get the number of generated WORDs for an opcode (or pseudoopcode).
 Parameters : opcode - pointer to opcode token (NULL if no opcode)
            : field  - address field for opcode
    Returns : The number of WORDs generated (0 or 1).
   Comments : Called in pass 1 only.
 ******************************************************************************/
static int
numgenwords(char *opcode, char *field)
{
    int  result = 0;

/******
 * If there is an opcode, handle it.
 ******/

    if (opcode != NULL)
    {
        if (STREQ(opcode, "ORG"))
        {
            result = 0;
        }
        else if (STREQ(opcode, "END"))
        {
            result = 0;
        }
        else	/* we assume opcode is OK, check in pass 2 */
        {
            result = 1;
        }
    }

/******
 * Return # generated words.
 ******/

    return result;
}


/******************************************************************************
       Name : Pass1()
Description : Perform first pass on a file.
 Parameters : 
    Returns : TRUE if no errors, else FALSE.
   Comments : Just define labels.  Leave most errors for pass 2.
 ******************************************************************************/
BOOL
Pass1(void)
{
    char buffer[BUFFERSIZE + 1];
    char *label;
    char *opcode;
    char *field;
    char *comment;
    int  i;
    int  genwords;

/******
 * Initialise the hash table, et al.
 ******/

    for (i = 0; i < HASHTABSIZE; ++i)
        hashtab[i] = NULL;

    LineNumber = 0;

    dot = -1L;

/******
 * Read and process the file.
 * Just fill in the symbol table (labels) as we go.
 ******/

    while (fgets(buffer, sizeof(buffer), InFile) != NULL)
    {
        ++LineNumber;

        strcpy(inputline, buffer);

        /* point 'label', 'opcode' and 'field' to strings */
        delimfields(buffer, &label, &opcode, &field, &comment);

        /* if there's something there, get # generated words */
        if (opcode != NULL)
        {
            if (STREQ(opcode, "END"))
                break;

            if (STREQ(opcode, "ORG"))
            {
                if (field == NULL || !isoctal(field))
                {
                    synerror(inputline, "Bad ORG adress");
                    return FALSE;
                }

                dot = atoo(field);
            }
            else
            {
                genwords = numgenwords(opcode, field);

                if (label != NULL)
                {
                    if (lookup(label))
                        synerror(inputline, "Label already defined");
                    deflabel(label, dot);
                }

                dot += genwords;
            }
        }
    }

    return TRUE;
}


/******************************************************************************
       Name : Pass2()
Description : Perform second pass on a file.
 Parameters : 
    Returns : 
   Comments : 
 ******************************************************************************/
BOOL
Pass2(void)
{
    char buffer[BUFFERSIZE + 1];
    char *label;
    char *opcode;
    char *field;
    char *comment;

/******
 * Initialize linenumber, et al.
 ******/

    LineNumber = 0;
    dot = -1L;

/******
 * Start the output - emit tape or tty block loader
 ******/

    emitloader();

/******
 * Read the file, generating code as we go.
 ******/

    while (fgets(buffer, sizeof(buffer), InFile) != NULL)
    {
        char *chptr;

        ++LineNumber;

        chptr = strrchr(buffer, '\r');
        if (chptr)
            strcpy(chptr, chptr + 1);

        strcpy(inputline, buffer);

        /* point 'label', 'opcode' and 'field' to strings */
        delimfields(buffer, &label, &opcode, &field, &comment);

        /* if there's something there, generate code */
        if (gencode(label, opcode, field, comment) == FALSE)
            break;		/* gencode() returns FALSE on 'END' pseudoop */
    }

/******
 * Check there is nothing after END statement.
 ******/

    if (fgets(buffer, sizeof(buffer), InFile) != NULL)
    {
        ++LineNumber;
        synerror(buffer, "Something after END!?");
        return FALSE;
    }

/******
 * Emit the  data.
 ******/

    emitblock();
    emitstart(WORDMASK);

    return TRUE;
}


/******************************************************************************
       Name : synerror()
Description : Generate a syntax error, then stop.
 Parameters : inputline - line that had error
            : fmt       - start of printf() style params
    Returns : Doesn't!
   Comments : 
 ******************************************************************************/
static void
synerror(char *inputline, char *fmt, ...)
{
    va_list ap;
    char    msg[1024];

    fprintf(stderr, "------------------------------------------------------\n");
    fprintf(stderr, "%s", inputline);
    fprintf(stderr, "------------------------------------------------------\n");

    va_start(ap, fmt);
    fprintf(stderr, "File %s, line %d: ", InFileName, LineNumber);
    vsprintf(msg, fmt, ap);
    fprintf(stderr, "%s\n", msg);
    va_end(ap);

    fflush(stderr);

    exit(EXIT_FAILURE);
}

#ifdef JUNK
/******************************************************************************
       Name : synwarn()
Description : Generate a syntax error, and continue.
 Parameters : fmt - start of printf() style params
    Returns : 
   Comments : 
 ******************************************************************************/
static void
synwarn(char *fmt, ...)
{
    va_list ap;
    char    msg[1024];

    va_start(ap, fmt);
    vsprintf(msg, fmt, ap);
    fprintf(stdout, "%s\n", msg);
    va_end(ap);

    fflush(stdout);
}
#endif


/******************************************************************************
       Name : strupper()
Description : Convert a string to uppercase, in situ.
 Parameters : str - address of string to convert
    Returns : 
   Comments : 
 ******************************************************************************/
static void
strupper(char *str)
{
    for (; *str; ++str)
        *str = toupper(*str);
}


#ifdef JUNK
/******************************************************************************
       Name : xemitcode()
Description : Emit papertape code.
 Parameters : fname - output filename (for error reporting)
            : out   - open FILE stream for output
    Returns : 
   Comments : 
 ******************************************************************************/
static void
xemitcode(char *fname, FILE *out)
{
    BLOCK *bptr;

    for (bptr = blocklist; bptr != NULL; bptr = bptr->next)
    {
        WORD checksum = (bptr->org + ((-bptr->nextword) & WORDMASK)) & WORDMASK;
        WORD i;

        for (i = 0; i < bptr->nextword; ++i)
            checksum = (checksum + bptr->code[i]) & WORDMASK;

        emitword(bptr->org);
        emitword(-bptr->nextword);
        emitword(checksum);

        for (i = 0; i < bptr->nextword; ++i)
            emitword(bptr->code[i]);

    }
}

#endif


