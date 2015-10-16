/*
 * Test the MEMORY implementation.
 */

#include <stdio.h>
#include <assert.h>

#include "vimlac.h"
#include "memory.h"


int
main(int argc, char *argv[])
{
    WORD addr;
    WORD result;
    FILE *fd;

    // test the "memory clear" function
    mem_clear();
    for (addr = 0; addr < MEM_SIZE; ++addr)
        assert(mem_get(addr, false) == 0);

    // write some data to memory, check written properly
    for (addr = 0; addr < MEM_SIZE; ++addr)
        mem_put(addr, false, addr);
    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        if (mem_get(addr, false) != addr)
        {
            printf("A: mem_get(0x%04x) was 0x%04x, should be 0x%04x\n",
                   addr, mem_get(addr, false), addr);
            return 1;
        }
    }

    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        mem_put(addr, false, (MEM_SIZE - addr));
    }
    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        if (mem_get(addr, false) != (MEM_SIZE - addr))
        {
            printf("B: mem_get(0x%04x) was 0x%04x, should be 0x%04x\n",
                   addr, mem_get(addr, false), addr);
            return 1;
        }
    }

    // now test auto-index locations
    mem_put(0, false, 0);
    mem_put(1, false, 1);
    mem_put(2, false, 2);
    mem_put(010, false, 0);
    result = mem_get(010, true);
    if (result != 1)
    {
	printf("C: auto-index at address 010 not indirectly addressing\n");
	return 1;
    }
    result = mem_get(010, false);
    if (result != 1)
    {
	printf("D: auto-index at address 010 not incrementing\n");
	return 1;
    }
    mem_put(010, false, 0xffff);
    result = mem_get(010, true);
    if (result != 0)
    {
	printf("E: auto-index at address 010 not indirectly addressing\n");
	return 1;
    }
    result = mem_get(010, false);
    if (result != 0)
    {
	printf("F: auto-index at address 010 not incrementing\n");
	return 1;
    }

    // check 017, make sure address wrap-around works
    mem_put(0, false, 2);
    mem_put(1, false, 1);
    mem_put(2, false, 0);
    mem_put(017, false, 1);
    result = mem_get(017, true);
    if (result != 0)
    {
	printf("G: auto-index at address 017 not indirectly addressing\n");
	return 1;
    }
    result = mem_get(017, false);
    if (result != 2)
    {
	printf("H: auto-index at address 017 not incrementing\n");
	return 1;
    }
    mem_put(017, false, 0x3fff);
    result = mem_get(017, true);
    if (result != 2)
    {
	printf("I: auto-index at address 017 not indirectly addressing\n");
	return 1;
    }
    result = mem_get(017, false);
    if (result != 0x4000)
    {
	printf("J: auto-index at address 017 not incrementing\n");
	return 1;
    }

    // now save memory to a file
    mem_set_rom_readonly(false);
    mem_clear();
    for (addr = 0; addr < MEM_SIZE; ++addr)
        mem_put(addr, false, addr);
    fd = fopen("imlac.core", "wb");
    mem_save_core(fd);
    fclose(fd);

    // clear memory and read core file back in
    mem_clear();
    fd = fopen("imlac.core", "rb");
    mem_load_core(fd);
    fclose(fd);
    for (addr = 0; addr < MEM_SIZE; ++addr)
    {
        if (mem_get(addr, false) != addr)
        {
            printf("K: mem_get(0x%04x) was 0x%04x, should be 0x%04x\n",
                   addr, mem_get(addr, false), addr);
            return 1;
        }
    }

    return 0;
}
