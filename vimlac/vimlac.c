/*
 * Miscellaneous routines for the vimlac machine.
 */

#include "vimlac.h"
#include "bootstrap.h"
#include "memory.h"
#include "ptrptp.h"
#include "cpu.h"


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


int
main(void)
{
    mem_clear(0);
    mem_set_rom(PtrROMImage);
    ptr_mount("test_add.ptp");
    run(040);
    run(0100);
    mem_save_core("vimlac.core");
}


