/*
 * Implementation of vimlac memory.
 *
 * Memory size is a compile-time constant.
 * The code here handles indirect memory references as will
 * as the 8 auto-index registers at 010-017 in every 2K block.
 */

#include <stdio.h>

#include "memory.h"


/*****
 * constants for the memory
 ******/

/* size of memory is 16K words */
#define ADDR_MASK	0x3fff

/* mask  and limits to check if address is auto-index register */
#define INDEX_MASK	03777
#define LOWER_INDEX	010
#define HIGHER_INDEX	017

/*****
 * State variables for the memory emulation
 ******/

#define ROM_START	040
#define ROM_END		077
#define ROM_SIZE	(ROM_END - ROM_START + 1)

static bool rom_readonly = false;

/* the physical memory */
static WORD memory[MEM_SIZE];

/******
 * Macro to decide if we are using an auto-index register
 ******/

#define AUTO_INDEX(a)	(((a & INDEX_MASK) >= LOWER_INDEX) && ((a & INDEX_MASK) <= HIGHER_INDEX))


WORD
mem_get(WORD address, bool indirect)
{
    WORD a = address & ADDR_MASK;	/* wrap address to physical memory */
    WORD result;

    if (indirect && AUTO_INDEX(a))	/* if auto-index and indirect, increment */
	memory[a] = (memory[a] + 1) & WORD_MASK;

    result = memory[a & ADDR_MASK];
    if (indirect)
	result = memory[result & ADDR_MASK];

    return result;
}

void
mem_put(WORD address, bool indirect, WORD value)
{
    WORD a = address & ADDR_MASK;	/* wrap address to physical memory */

    if (indirect && AUTO_INDEX(a))	/* if auto-index and indirect, increment */
	memory[a] = (memory[a] + 1) & WORD_MASK;

    if (indirect)
	a = memory[a & ADDR_MASK];

    memory[a & ADDR_MASK] = value;
}

void
mem_clear(void)
{
    if (rom_readonly)
    {	/* save the ROM contents */
        WORD rom[ROM_SIZE];

        memcpy(rom, &memory[ROM_START], sizeof(WORD)*ROM_SIZE);
        memset(memory, 0, sizeof(WORD)*MEM_SIZE);
        memcpy(&memory[ROM_START], rom, sizeof(WORD)*ROM_SIZE);
    }
    else
        memset(memory, 0, sizeof(WORD)*MEM_SIZE);
}

void
mem_set_rom(WORD *rom)
{
    rom_readonly = true;
    memcpy(&memory[ROM_START], rom, sizeof(WORD)*ROM_SIZE);
}

void
mem_set_rom_readonly(bool readonly)
{
    rom_readonly = readonly;
}

void
mem_load_core(char *filename)
{
    FILE *fd = fopen(filename, "rb");
    WORD addr;

    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        unsigned char byte1;
        unsigned char byte2;
        WORD value;

	fread(&byte1, 1, 1, fd);
	fread(&byte2, 1, 1, fd);
	value = (byte1 << 8) + byte2;
	memory[addr] = value;
    }

    fclose(fd);
}

void
mem_save_core(char *filename)
{
    FILE *fd = fopen(filename, "wb");
    WORD addr;

    /* write memory in bytes, get around endian problems */
    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        unsigned char byte;
        WORD value;

	value = memory[addr];
	byte = (value >> 8) & 0xff;
	fwrite(&byte, 1, 1, fd);
	byte = value & 0xff;
	fwrite(&byte, 1, 1, fd);
    }

    fclose(fd);
}
