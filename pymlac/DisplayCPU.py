#!/usr/bin/python

"""
The Imlac display CPU.
"""


import sys

from Globals import *
import Trace


class DisplayCPU(object):

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

    # global state variables
    Mode = MODE_NORMAL
    Running = False


    def __init__(self, display, memory):
        self.Mode = self.MODE_NORMAL
        self.Running = False

        self.display = display
        self.memory = memory

    def DEIMdecode(self, byte):
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

    def doDEIMByte(self, byte):
        if byte & 0x80:			# increment?
            prevDX = self.DX
            prevDY = self.DY
            if byte & 0x20:
                self.DX -= (byte & 0x18) >> 3
            else:
                self.DX += (byte & 0x18) >> 3
            if byte & 0x04:
                self.DY -= (byte & 0x03)
            else:
                self.DY += (byte & 0x03)
                if byte & 0x40:
                    self.display.draw(prevDX, prevDY, self.DX, self.DY)
        else:				# micro instructions
            if byte & 0x40:
                self.Mode = self.self.MODE_NORMAL
            if byte & 0x20:		# DRJM
                if self.DRSindex <= 0:
                    Trace.comment('\nDRS stack underflow at display address %6.6o'
                                  % (self.DPC - 1))
                    self.illegal()
                self.DRSindex -= 1
                self.DPC = DRS[DRSindex]
            if byte & 0x10:
                self.DX += 0x08
            if byte & 0x08:
                self.DX &= 0xfff8
            if byte & 0x02:
                self.DY += 0x10
            if byte & 0x01:
                self.DY &= 0xfff0

    def execute_one_instruction(self):
        if not self.Running:
            Trace.dtrace('')
            return 0

        instruction = self.memory.get(self.DPC, 0)
        self.DPC = MASK_MEM(self.DPC + 1)

        if self.Mode == self.MODE_DEIM:
            Trace.trace(self.DEIMdecode(instruction >> 8) + '\t')
            self.doDEIMByte(instruction >> 8)
            if self.Mode == self.MODE_DEIM:
                Trace.trace(self.DEIMdecode(instruction & 0xff) + '\t')
                self.doDEIMByte(instruction & 0xff)
            else:
                Trace.trace('\t')
            return 1

        opcode = instruction >> 12
        address = instruction & 007777

        if   opcode == 000: return self.page00(instruction)
        elif opcode == 001: return self.i_DLXA(address)
        elif opcode == 002: return self.i_DLYA(address)
        elif opcode == 003: return self.i_DEIM(address)
        elif opcode == 004: return self.i_DLVH(address)
        elif opcode == 005: return self.i_DJMS(address)
        elif opcode == 006: return self.i_DJMP(address)
        elif opcode == 007: self.illegal(instruction)
        else:               self.illegal(instruction)

    def illegal(self, instruction=None):
        if instruction:
            Trace.comment('Illegal display instruction (%6.6o) at address %6.6o'
                          % (instruction, (self.DPC - 1)))
        else:
            Trace.comment('Illegal display instruction at address %6.6o'
                          % (self.DPC - 1))
        sys.exit(0)

    def ison(self):
        return self.Running

    def i_DDXM(self):
        self.DX -= 040
        Trace.dtrace('DDXM')

    def i_DDYM(self):
        self.DY -= 040
        Trace.dtrace('DDYM')

    def i_DEIM(self, address):
        self.Mode = self.MODE_DEIM
        Trace.deimtrace('DEIM', self.DEIMdecode(address & 0377))
        self.doDEIMByte(address & 0377)
        return 1

    def i_DHLT(self):
        self.Running = False
        Trace.dtrace('DHLT')

    def i_DHVC(self):
        Trace.dtrace('DHVC')

    def i_DIXM(self):
        self.DX += 04000
        Trace.dtrace('DIXM')

    def i_DIYM(self):
        self.DY += 04000
        Trace.dtrace('DIYM')

    def i_DJMP(self, address):
        self.DPC = MASK_MEM(address + (self.DIB << 12))
        Trace.dtrace('DJMP', address)
        return 1

    def i_DJMS(self, address):
        if self.DRSindex >= 8:
            Trace.comment('DRS stack overflow at display address %6.6o'
                          % (self.DPC - 1))
            self.illegal()
        self.DRS[self.DRSindex] = self.DPC
        self.DRSindex += 1
        self.DPC = MASK_MEM(address + (self.DIB << 12))
        Trace.dtrace('DJMS', address)
        return 1

    def i_DLXA(self, address):
        self.DX = address
        Trace.dtrace('DLXA', address)
        return 1

    def i_DLYA(self, address):
        self.DY = address
        Trace.dtrace('DLYA', address)
        return 1

    def i_DLVH(self, word1):
        word2 = self.memory.get(self, DPC, 0)
        self.DPC = MASK_MEM(self.DPC + 1)
        word3 = self.memory.get(self.DPC, 0)
        self.DPC = MASK_MEM(self.DPC + 1)

        dotted = word2 & 040000
        beamon = word2 & 020000
        negx = word3 & 040000
        negy = word3 & 020000
        ygtx = word3 & 010000

        M = word2 & 007777
        N = word3 & 007777

        prevDX = self.DX
        prevDY = self.DY

        if ygtx:		# M is y, N is x
            if negx:
                self.DX -= N
            else:
                self.DX += N
            if negy:
                self.DY -= M
            else:
                self.DY += M
        else:			# M is x, N is y
            if negx:
                self.DX -= M
            else:
                self.DX += M
            if negy:
                self.DY -= N
            else:
                self.DY += N

            self.display.draw(prevDX, prevDY, self.DX, self.DY, dotted)
        Trace.dtrace('DLVH')
        return 3

    def i_DRJM(self):
        if self.DRSindex <= 0:
           Trace.comment('DRS stack underflow at display address %6.6o'
                         % (self.DPC - 1))
           self.illegal()
        self.DRSindex -= 1
        self.DPC = self.DRS[self.DRSindex]
        Trace.dtrace('DRJM')
        return 1        # FIXME check # cycles used

    def i_DSTB(self, block):
        self.DIB = block
        Trace.dtrace('DSTB\t%d' % block)

    def i_DSTS(self, scale):
        if scale == 0:
            self.Scale = 0.5
        elif scale == 1:
            self.Scale = 1.0
        elif scale == 2:
            self.Scale = 2.0
        elif scale == 3:
            self.Scale = 3.0
        else:
            self.illegal()
        Trace.dtrace('DSTS', scale)
        return 1        # FIXME check # cycles used

    def page00(self, instruction):
        if instruction == 000000:		# DHLT
            self.i_DHLT()
        elif instruction == 004000:		# DNOP
            Trace.dtrace('DNOP')
        elif instruction == 004004:		# DSTS 0
            self.i_DSTS(0)
        elif instruction == 004005:		# DSTS 1
            self.i_DSTS(1)
        elif instruction == 004006:		# DSTS 2
            self.i_DSTS(2)
        elif instruction == 004007:		# DSTS 3
            self.i_DSTS(3)
        elif instruction == 004010:		# DSTB 0
            self.i_DSTB(0)
        elif instruction == 004011:		# DSTB 1
            self.i_DSTB(1)
        elif instruction == 004040:		# DRJM
            self.i_DRJM()
        elif instruction == 004100:		# DDYM
            self.i_DDYM()
        elif instruction == 004200:		# DDXM
            self.i_DDXM()
        elif instruction == 004400:		# DIYM
            self.i_DIYM()
        elif instruction == 005000:		# DIXM
            self.i_DIXM()
        elif instruction == 006000:		# DHVC
            self.i_DHVC()
        else:
            self.illegal(instruction)
        return 1

    def start(self):
        self.Running = True

    def stop(self):
        self.Running = False
