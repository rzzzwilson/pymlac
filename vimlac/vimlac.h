/*
 * Interface for the vimlac emulator.
 */

#ifndef VIMLAC_H
#define VIMLAC_H

#include <stddef.h>
#include <stdio.h>
#include <stdbool.h>
#include <stdarg.h>
#include <string.h>
#include <errno.h>

#include "error.h"


#define VIMLAC_VERSION  "0.1"

typedef unsigned int	WORD;
typedef unsigned char	BYTE;

#define MEMORY_SIZE     04000

#define CPU_HERZ	1800000
#define MEMMASK		0xffff
#define HIGHBITMASK	0x8000
#define WORD_MASK	0xffff
#define OVERFLOWMASK	0x10000
#define LOWBITMASK	0x1

// macro to convert a boolean value to a string
#define BOOL2STR(a)     ((a) ? "true" : "false")

// macro to more reliably compare strings
#define STREQ(a, b) ((a) && (strcmp((a), (b)) == 0))

// macro to mask an address to the address space limits
#define MASK_MEM(addr) (addr & (MEMORY_SIZE - 1))


#endif
