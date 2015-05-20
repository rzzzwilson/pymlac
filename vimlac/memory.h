/*
 * Interface for the vimlac memory.
 */

#ifndef MEMORY_H
#define MEMORY_H

#include "vimlac.h"

#define MEM_SIZE	0x4000

WORD mem_get(WORD address, bool indirect);
void mem_put(WORD address, bool indirect, WORD value);

void mem_clear(void);
void mem_set_rom(WORD *rom);
void mem_set_rom_readonly(bool readonly);
void mem_load_core(char *filename);
void mem_save_core(char *filename);

#endif
