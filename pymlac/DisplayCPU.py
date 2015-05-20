#!/usr/bin/python

"""
The Imlac display CPU.
"""


import sys

from Globals import *
import Trace


# display CPU constants
MODE_NORMAL = 0
MODE_DEIM = 1

######
# The Display CPU registers
######

DPC = 0				# display CPU program counter
DRS = [0, 0, 0, 0, 0, 0, 0, 0]	# display CPU ???
DRSindex = 0			# display CPU ???
DIB = 0				# display CPU ???
DX = 0				# display CPU draw X register
DY = 0				# display CPU draw Y register

# state variables
mode = MODE_NORMAL
running = False



def init():
    mode = MODE_NORMAL
    running = False

def DEIMdecode(byte):
    """Decode a DEIM byte"""

    result = ''
    if byte & 0x80:
        if byte & 0x40: result += 'B'
        else:           result += 'D'
        if byte & 0x20: result += '-'
        result += '%d' % ((byte >> 3) & 0x03)
        if byte & 0x04: result += '-'
        result += '%d' % (byte & 0x03)
    else:
        if byte == 0111:   result += 'N'
        elif byte == 0151: result += 'R'
        elif byte == 0171: result += 'F'
        elif byte == 0200: result += 'P'
        else:              result += 'A%3.3o' % byte
    return result

def doDEIMByte(byte):
    global DPC, DX, DY, DRSindex

    if byte & 0x80:			# increment?
        prevDX = DX
        prevDY = DY
        if byte & 0x20:
            DX -= (byte & 0x18) >> 3
        else:
            DX += (byte & 0x18) >> 3
        if byte & 0x04:
            DY -= (byte & 0x03)
        else:
            DY += (byte & 0x03)
#            if byte & 0x40:
#                display.draw(0, prevDX, prevDY, DX, DY)
    else:				# micro instructions
        if byte & 0x40:
            mode = MODE_NORMAL
        if byte & 0x20:		# DRJM
            if DRSindex <= 0:
                Trace.comment('\nDRS stack underflow at display address %6.6o'
                              % (DPC - 1))
                illegal()
            DRSindex -= 1
            DPC = DRS[DRSindex]
        if byte & 0x10:
            DX += 0x08
        if byte & 0x08:
            DX &= 0xfff8
        if byte & 0x02:
            DY += 0x10
        if byte & 0x01:
            DY &= 0xfff0

def execute_one_instruction():
    global DPC

    if not running:
        Trace.dtrace('')
        return 0

    instruction = Memory.get(DPC, 0)
    DPC = MASK_MEM(DPC + 1)

    if mode == MODE_DEIM:
        Trace.trace(DEIMdecode(instruction >> 8) + '\t')
        doDEIMByte(instruction >> 8)
        if mode == MODE_DEIM:
            Trace.trace(DEIMdecode(instruction & 0xff) + '\t')
            doDEIMByte(instruction & 0xff)
        else:
            Trace.trace('\t')
        return 1

    opcode = instruction >> 12
    address = instruction & 007777

    if   opcode == 000:	return page00(instruction)
    elif opcode == 001:     return i_DLXA(address)
    elif opcode == 002:     return i_DLYA(address)
    elif opcode == 003:     return i_DEIM(address)
    elif opcode == 004:     return i_DLVH(address)
    elif opcode == 005:     return i_DJMS(address)
    elif opcode == 006:     return i_DJMP(address)
    elif opcode == 007:     return illegal(instruction)
    else:                   illegal(instruction)

def illegal(instruction=None):
    if instruction:
        Trace.comment('Illegal display instruction (%6.6o) at address %6.6o'
                      % (instruction, (DPC - 1)))
    else:
        Trace.comment('Illegal display instruction at address %6.6o'
                      % (DPC - 1))
    sys.exit(0)

def ison():
    return running

def i_DDXM():
    global DX

    DX -= 040
    Trace.dtrace('DDXM')

def i_DDYM():
    global DY

    DY -= 040
    Trace.dtrace('DDYM')

def i_DEIM(address):
    mode = MODE_DEIM
    Trace.deimtrace('DEIM', DEIMdecode(address & 0377))
    doDEIMByte(address & 0377)
    return 1

def i_DHLT():
    running = False
    Trace.dtrace('DHLT')

def i_DHVC():
    Trace.dtrace('DHVC')

def i_DIXM():
    global DX

    DX += 04000
    Trace.dtrace('DIXM')

def i_DIYM():
    global DY

    DY += 04000
    Trace.dtrace('DIYM')

def i_DJMP(address):
    global DPC, DIB

    DPC = MASK_MEM(address + (DIB << 12))
    Trace.dtrace('DJMP', address)
    return 1

def i_DJMS(address):
    global DPC, DRSindex, DIB

    if DRSindex >= 8:
        Trace.comment('DRS stack overflow at display address %6.6o'
                      % (DPC - 1))
        illegal()
    DRS[DRSindex] = DPC
    DRSindex += 1
    DPC = MASK_MEM(address + (DIB << 12))
    Trace.dtrace('DJMS', address)
    return 1

def i_DLXA(address):
    global DX

    DX = address
    Trace.dtrace('DLXA', address)
    return 1

def i_DLYA(address):
    global DY

    DY = address
    Trace.dtrace('DLYA', address)
    return 1

def i_DLVH(word1):
    global DPC, DX, DY

    word2 = Memory.get(DPC, 0)
    DPC = MASK_MEM(DPC + 1)
    word3 = Memory.get(DPC, 0)
    DPC = MASK_MEM(DPC + 1)

    dotted = word2 & 040000
    beamon = word2 & 020000
    negx = word3 & 040000
    negy = word3 & 020000
    ygtx = word3 & 010000

    M = word2 & 007777
    N = word3 & 007777

    prevDX = DX
    prevDY = DY

    if ygtx:		# M is y, N is x
        if negx:
            DX -= N
        else:
            DX += N
        if negy:
            DY -= M
        else:
            DY += M
    else:			# M is x, N is y
        if negx:
            DX -= M
        else:
            DX += M
        if negy:
            DY -= N
        else:
            DY += N

#        display.drawline(dotted, prevDX, prevDY, DX, DY)
    Trace.dtrace('DLVH')
    return 3

def i_DRJM():
    global DPC, DRSindex

    if DRSindex <= 0:
       Trace.comment('DRS stack underflow at display address %6.6o'
                     % (DPC - 1))
       illegal()
    DRSindex -= 1
    DPC = DRS[DRSindex]
    Trace.dtrace('DRJM')

def i_DSTB(block):
    global DIB

    DIB = block
    Trace.dtrace('DSTB\t%d' % block)

def i_DSTS(scale):
    global Scale

    if scale == 0:
        Scale = 0.5
    elif scale == 1:
        Scale = 1.0
    elif scale == 2:
        Scale = 2.0
    elif scale == 3:
        Scale = 3.0
    else:
        illegal()
    Trace.dtrace('DSTS', scale)

def page00(instruction):
    if instruction == 000000:		# DHLT
        i_DHLT()
    elif instruction == 004000:		# DNOP
        Trace.dtrace('DNOP')
    elif instruction == 004004:		# DSTS 0
        i_DSTS(0)
    elif instruction == 004005:		# DSTS 1
        i_DSTS(1)
    elif instruction == 004006:		# DSTS 2
        i_DSTS(2)
    elif instruction == 004007:		# DSTS 3
        i_DSTS(3)
    elif instruction == 004010:		# DSTB 0
        i_DSTB(0)
    elif instruction == 004011:		# DSTB 1
        i_DSTB(1)
    elif instruction == 004040:		# DRJM
        i_DRJM()
    elif instruction == 004100:		# DDYM
        i_DDYM()
    elif instruction == 004200:		# DDXM
        i_DDXM()
    elif instruction == 004400:		# DIYM
        i_DIYM()
    elif instruction == 005000:		# DIXM
        i_DIXM()
    elif instruction == 006000:		# DHVC
        i_DHVC()
    else:
        illegal(instruction)
    return 1

def start():
    global running

    running = True

def stop():
    global running

    running = False
