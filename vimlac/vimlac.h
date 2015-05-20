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

typedef unsigned int	WORD;
typedef unsigned char	BYTE;

#define CPU_HERZ	1800000
#define MEMMASK		0xffff
#define HIGHBITMASK	0x8000
#define WORD_MASK	0xffff
#define OVERFLOWMASK	0x10000
#define LOWBITMASK	0x1


void error(char *msg, ...);

#endif
