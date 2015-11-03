/*
 * Miscellaneous routines for the vimlac machine.
 */

#include "vimlac.h"
#include "memory.h"
#include "ptr.h"
#include "cpu.h"


void
error(char *msg, ...)
{
    return;
}

WORD PtrROMImage[] = {0060077, /* start  lac    base  ;40 get load address */
                      0020010, /*        dac    10    ;41 put into auto-inc reg */
                      0104100, /*        lwc    0100  ;42 -0100 into AC */
                      0020020, /*        dac    20    ;43 put into memory */
                      0001061, /*        hon          ;44 start PTR */
                      0100011, /* wait   cal          ;45 clear AC+LINK */
                      0002400, /*        hsf          ;46 skip if PTR has data */
                      0010046, /*        jmp    .-1   ;47 wait until is data */
                      0001051, /*        hrb          ;50 read PTR -> AC */
                      0074075, /*        sam    what  ;51 skip if AC == 2 */
                      0010045, /*        jmp    wait  ;52 wait until PTR return 0 */
                      0002400, /* loop   hsf          ;53 skip if PTR has data */
                      0010053, /*        jmp    .-1   ;54 wait until is data */
                      0001051, /*        hrb          ;55 read PTR -> AC */
                      0003003, /*        ral    3     ;56 move byte into high AC */
                      0003003, /*        ral    3     ;57 */
                      0003002, /*        ral    2     ;60 */
                      0102400, /*        hsn          ;61 wait until PTR moves */
                      0010061, /*        jmp    .-1   ;62 */
                      0002400, /*        hsf          ;63 skip if PTR has data */
                      0010063, /*        jmp    .-1   ;64 wait until is data */
                      0001051, /*        hrb          ;65 read PTR -> AC */
                      0120010, /*        dac    *10   ;66 store word, inc pointer */
                      0102400, /*        hsn          ;67 wait until PTR moves */
                      0010067, /*        jmp    .-1   ;70 */
                      0100011, /*        cal          ;71 clear AC & LINK */
                      0030020, /*        isz    20    ;72 inc mem and skip zero */
                      0010053, /*        jmp    loop  ;73 if not finished, jump */
                      0110076, /*        jmp    *go   ;74 execute loader */
                      0000002, /* what   data   2     ;75 */
                      0003700, /* go     word   03700H;76 */
                      0003677  /* base   word   03677H;77 */};

WORD TtyROMImage[] = {0060077, /* start  lac    base  ;40 get load address */
                      0020010, /*        dac    10    ;41 put into auto-inc reg */
                      0104100, /*        lwc    0100  ;42 -0100 into AC */
                      0020020, /*        dac    20    ;43 put into memory */
                      0001061, /*        hon          ;44 start PTR */
                      0100011, /* wait   cal          ;45 clear AC+LINK */
                      0002400, /*        hsf          ;46 skip if PTR has data */
                      0010046, /*        jmp    .-1   ;47 wait until is data */
                      0001051, /*        hrb          ;50 read PTR -> AC */
                      0074075, /*        sam    what  ;51 skip if AC == 2 */
                      0010045, /*        jmp    wait  ;52 wait until PTR return 0 */
                      0002400, /* loop   hsf          ;53 skip if PTR has data */
                      0010053, /*        jmp    .-1   ;54 wait until is data */
                      0001051, /*        hrb          ;55 read PTR -> AC */
                      0003003, /*        ral    3     ;56 move byte into high AC */
                      0003003, /*        ral    3     ;57 */
                      0003002, /*        ral    2     ;60 */
                      0102400, /*        hsn          ;61 wait until PTR moves */
                      0010061, /*        jmp    .-1   ;62 */
                      0002400, /*        hsf          ;63 skip if PTR has data */
                      0010063, /*        jmp    .-1   ;64 wait until is data */
                      0001051, /*        hrb          ;65 read PTR -> AC */
                      0120010, /*        dac    *10   ;66 store word, inc pointer */
                      0102400, /*        hsn          ;67 wait until PTR moves */
                      0010067, /*        jmp    .-1   ;70 */
                      0100011, /*        cal          ;71 clear AC & LINK */
                      0030020, /*        isz    20    ;72 inc mem and skip zero */
                      0010053, /*        jmp    loop  ;73 if not finished, jump */
                      0110076, /*        jmp    *go   ;74 execute loader */
                      0000002, /* what   data   2     ;75 */
                      0003700, /* go     word   03700H;76 */
                      0003677  /* base   word   03677H;77 */};

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


