#!/usr/bin/python

"""
The Imlac display CPU.

The Imlac dislay X and Y registers are of size 11 bits.  The most significant
6 bits are the MSB and the least significant 5 bits are the LSB.  A DLXA (or
DLYA) loads the display X (or Y) register from the 10 bits of valu, with bit
10 of the X/Y register being set to 0.

The display is 2048x2048 pixels.
"""


import sys

from Globals import *
import Trace


trace = Trace.Trace(TRACE_FILENAME)

import log
log = log.Log('test.log', log.Log.DEBUG)


# constants
MSBBITS = 6
LSBBITS = 5

MSBMASK = 03740
LSBMASK = 037


class DisplayCPU(object):

    # mask for display address
    DMASK = 03777                       # full 11 bits of display addressing
    BITS10 = 01777                      # AC bits that set DX or DY
    DMSB = 03740
    DLSB = 037

    # display CPU constants - modes
    MODE_NORMAL = 0
    MODE_DEIM = 1

    ######
    # The Display CPU registers
    ######

    DPC = 0				# display CPU program counter
    DRS = [0, 0, 0, 0, 0, 0, 0, 0]	# display CPU stack
    DRSindex = 0			# display CPU ???
    DIB = 0				# display CPU ???
    DX = 0				# display CPU draw X register
    DY = 0				# display CPU draw Y register
    DScale = 4                          # display scale (1, 2, 4, 8)

    # global state variables
    Mode = MODE_NORMAL
    Running = False


    def __init__(self, display, memory):
        self.Mode = self.MODE_NORMAL
        self.Running = False

        self.display = display
        self.memory = memory

        self.dot = self.DPC

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

    def doDEIMByte(self, byte, last=False):
        """Execute a DEIM instruction byte.

        byte  is the byte to execute in DEIM mode
        last  True if the last byte in a word
        """

        trace = self.DEIMdecode(byte)
        log('doDEIMByte: trace=%s' % str(trace))

        if byte & 0x80:			# increment mode
            dx = (byte & 0x18) >> 3     # extract X/Y deltas
            dy = (byte & 0x03)

            prevDX = self.DX            # save previous position
            prevDY = self.DY

            if byte & 0x20:             # get dx sign and move X
                self.DX -= dx * self.DScale
            else:
                self.DX += dx * self.DScale

            if byte & 0x04:             # get dy sign and move Y
                self.DY -= dy * self.DScale
            else:
                self.DY += dy * self.DScale

            if byte & 0x40:             # if beam on
                self.display.draw(prevDX, prevDY, self.DX, self.DY)
        else:				# control instructions
            if byte & 0x40:             # escape DEIM mode
                self.Mode = self.MODE_NORMAL

            if byte & 0x20:		# DRJM
                if self.DRSindex <= 0:
                    trace.comment('\nDRS stack underflow at display address %6.6o'
                                  % (self.DPC - 1))
                    self.illegal()
                self.DRSindex -= 1
                self.DPC = self.DRS[self.DRSindex]

            if byte & 0x10:             # inc X MSB
                log('**** inc X MSB: before .DX=%d' % self.DX)
                self.DX += (1 << LSBBITS)
                log('**** inc X MSB:  after .DX=%d' % self.DX)

            if byte & 0x08:             # clear X LSB
                log('**** clear X LSB: before .DX=%d' % self.DX)
                self.DX &= MSBMASK
                log('**** clear X LSB:  after .DX=%d' % self.DX)

            if byte & 0x02:             # inc Y MSB
                log('**** inc Y MSB: before .DY=%d' % self.DY)
                self.DY += (1 << LSBBITS)
                log('**** inc Y MSB:  after .DY=%d' % self.DY)

            if byte & 0x01:             # clear Y LSB
                log('**** clear Y LSB: before .DY=%d' % self.DY)
                self.DY &= MSBMASK
                log('**** clear Y LSB:  after .DY=%d' % self.DY)

        return trace

    def execute_one_instruction(self):
        if not self.Running:
            return (0, None)

        self.dot = self.DPC
        instruction = self.memory.fetch(self.DPC, False)
        self.DPC = MASK_MEM(self.DPC + 1)

        if self.Mode == self.MODE_DEIM:
            tracestr = self.doDEIMByte(instruction >> 8)
            if self.Mode == self.MODE_DEIM:
                tracestr += ', ' + self.doDEIMByte(instruction & 0xff, True)
            log('execute_one_instruction: tracestr=%s' % tracestr)
            return (1, tracestr)

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
            trace.comment('Illegal display instruction (%6.6o) at address %6.6o'
                          % (instruction, (self.DPC - 1)))
        else:
            trace.comment('Illegal display instruction at address %6.6o'
                          % (self.DPC - 1))
        sys.exit(0)

    def ison(self):
        return self.Running

    def i_DDXM(self):
        self.DX -= 040
        tracestr = trace.dtrace(self.dot, 'DDXM', None)
        return (1, tracestr)

    def i_DDYM(self):
        self.DY -= 040
        tracestr = trace.dtrace(self.dot, 'DDYM', None)
        return (1, tracestr)

    def i_DEIM(self, address):
        self.Mode = self.MODE_DEIM
        tracestr = 'DEIM\t' + self.doDEIMByte(address & 0377, last=True)
        return (1, tracestr)

    def i_DHLT(self):
        self.Running = False
        return (1, trace.dtrace(self.dot, 'DHLT', None))

    def i_DHVC(self):
        return (1, trace.dtrace(self.dot, 'DHVC', None))

    def i_DIXM(self):
        self.DX += 04000
        return (1, trace.dtrace(self.dot, 'DIXM', None))

    def i_DIYM(self):
        self.DY += 04000
        return (1, trace.dtrace(self.dot, 'DIYM', None))

    def i_DJMP(self, address):
        self.DPC = MASK_MEM(address + (self.DIB << 12))
        return (1, trace.dtrace(self.dot, 'DJMP', address))

    def i_DJMS(self, address):
        if self.DRSindex >= 8:
            Trace.comment('DRS stack overflow at display address %6.6o'
                          % (self.DPC - 1))
            self.illegal()
        self.DRS[self.DRSindex] = self.DPC
        self.DRSindex += 1
        self.DPC = MASK_MEM(address + (self.DIB << 12))
        return (1, trace.dtrace(self.dot, 'DJMS', address))

    def i_DLXA(self, address):
        self.DX = (address & self.BITS10) << 1
        return (1, trace.dtrace(self.dot, 'DLXA', address))

    def i_DLYA(self, address):
        self.DY = (address & self.BITS10) << 1
        return (1, trace.dtrace(self.dot, 'DLXA', address))

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
        return (3, trace.dtrace(self.dot, 'DLVH', None))

    def i_DRJM(self):
        if self.DRSindex <= 0:
           Trace.comment('DRS stack underflow at display address %6.6o'
                         % (self.DPC - 1))
           self.illegal()
        self.DRSindex -= 1
        self.DPC = self.DRS[self.DRSindex]
        return (1, trace.dtrace(self.dot, 'DRJM', None)) # FIXME check # cycles used

    def i_DSTB(self, block):
        self.DIB = block
        trace.dtrace('DSTB\t%d' % block)
        return (1, trace.dtrace('DSTB\t%d' % block, None))

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
        return (1, trace.dtrace('DSTS\t%d' % scale, None)) # FIXME check # cycles used

    def page00(self, instruction):
        if instruction == 000000:		# DHLT
            (cycles, tracestr) = self.i_DHLT()
        elif instruction == 004000:		# DNOP
            cycles = 1
            tracestr = trace.dtrace('DNOP')
        elif instruction == 004004:		# DSTS 0
            (cycles, tracestr) = self.i_DSTS(0)
        elif instruction == 004005:		# DSTS 1
            (cycles, tracestr) = self.i_DSTS(1)
        elif instruction == 004006:		# DSTS 2
            (cycles, tracestr) = self.i_DSTS(2)
        elif instruction == 004007:		# DSTS 3
            (cycles, tracestr) = self.i_DSTS(3)
        elif instruction == 004010:		# DSTB 0
            (cycles, tracestr) = self.i_DSTB(0)
        elif instruction == 004011:		# DSTB 1
            (cycles, tracestr) = self.i_DSTB(1)
        elif instruction == 004040:		# DRJM
            (cycles, tracestr) = self.i_DRJM()
        elif instruction == 004100:		# DDYM
            (cycles, tracestr) = self.i_DDYM()
        elif instruction == 004200:		# DDXM
            (cycles, tracestr) = self.i_DDXM()
        elif instruction == 004400:		# DIYM
            (cycles, tracestr) = self.i_DIYM()
        elif instruction == 005000:		# DIXM
            (cycles, tracestr) = self.i_DIXM()
        elif instruction == 006000:		# DHVC
            (cycles, tracestr) = self.i_DHVC()
        else:
            self.illegal(instruction)
        return (cycles, tracestr)

    def start(self):
        self.Running = True

    def stop(self):
        self.Running = False
