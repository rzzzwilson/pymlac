#!/usr/bin/python

"""
Globals used throughout the emulator.
"""


# Version of the emulator
PYMLAC_VERSION = 'pymlac 0.1'

# Some colours
BLACK = (0,0,0)
WHITE = (255,255,255)
YELLOW = (255,255,64)
GREY = (128,128,128)
LIGHTGREY = (182,182,182)
RED = (128, 0, 0)

# various screen size values
CANVAS_WIDTH = 1024
CANVAS_HEIGHT = 1024

# 'core' size (words) and save filename
CORE_FILENAME = 'pymlac.core'
#MEMORY_SIZE = 040000	# 16K words memory size
MEMORY_SIZE = 0o4000	# 2K words memory size - while debugging
                        # removes some block address bugs
PCMASK = MEMORY_SIZE - 1

# Trace stuff
TRACE_FILENAME = 'pymlac.trace'

# Number of emulator cycles per second
CYCLES_PER_SECOND = int(1000000 / 1.8)

# Definitions of boot ROM code type
ROM_PTR = 'ptr'
ROM_TTY = 'tty'
ROM_NONE = None

# The 4K 'local' mask to remove high bits
ADDRHIGHMASK = 0x7800

# word overflow and value masks
OVERFLOWMASK = 0xffff0000
WORDMASK = 0xffff
HIGHBITMASK = 0x8000
#ADDRMASK = 0x7fff
ADDRMASK = 0o37777

# global instruction cycle counter
#instruction_cycles = 0

# trace flag
tracing = 1

# logging flag
logging = 1

# A function to mask values to Imlac word width
def MASK_16(value):
    return value & 0xffff

# A function to mask addresses to Imlac max memory address
def MASK_MEM(address):
    return address & (MEMORY_SIZE - 1)

# A function to decide if an address is an auto-increment address
def ISAUTOINC(address):
    maskaddr = address & 0o3777
    return (maskaddr >= 0o10) and (maskaddr <= 0o17)

