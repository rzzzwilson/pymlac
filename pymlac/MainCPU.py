#!/usr/bin/python

"""
The Imlac main CPU.
"""


import sys

from Globals import *
import Trace

import log
log = log.Log('test.log', log.Log.DEBUG)

trace = Trace.Trace(TRACE_FILENAME)


class MainCPU(object):

    ######
    # The main CPU registers
    ######

    PC = None           # main CPU program counter
    L = 0               # main CPU link register
    AC = 0              # main CPU accumulator
    Sync40Hz = 1        # main CPU 40Hz flag register
    DS = 0              # dataswitches value

    # address of base of local code block
    BlockBase = 0

    # decode dictionaries (initialized in __init__())
    main_decode = None
    page_00_decode = None
    page02_decode = None
    micro_opcodes = None
    micro_singles = None

    # module-level state variables
    running = False     # True if CPU running


    def __init__(self, memory, display, displaycpu, kbd, ttyin, ttyout, ptrptp):
        """Initialize the main CPU."""

        log('MainCPU.__init__: memory=%s' % str(memory))
        log('MainCPU.__init__: display=%s' % str(display))
        log('MainCPU.__init__: displaycpu=%s' % str(displaycpu))

        self.memory = memory
        self.display = display
        self.displaycpu = displaycpu
        self.kbd = kbd
        self.ttyin = ttyin
        self.ttyout = ttyout
        self.ptrptp = ptrptp

        # main dispatch dictionary for decoding opcodes in bits 1-4
        self.main_decode = {0o00: self.page_00,	# secondary decode
                            0o01: self.i_LAW_LWC,
                            0o02: self.i_JMP,
        #                   0o03: self.illegal,
                            0o04: self.i_DAC,
                            0o05: self.i_XAM,
                            0o06: self.i_ISZ,
                            0o07: self.i_JMS,
        #                   0o10: self.illegal
                            0o11: self.i_AND,
                            0o12: self.i_IOR,
                            0o13: self.i_XOR,
                            0o14: self.i_LAC,
                            0o15: self.i_ADD,
                            0o16: self.i_SUB,
                            0o17: self.i_SAM}

        # page_00 dispatch dictionary for decoding opcodes
        # HLT may be handled specially
        self.page_00_decode = {0o01003: self.i_DLA,
                               0o01011: self.i_CTB,
                               0o01012: self.i_DOF,
                               0o01021: self.i_KRB,
                               0o01022: self.i_KCF,
                               0o01023: self.i_KRC,
                               0o01031: self.i_RRB,
                               0o01032: self.i_RCF,
                               0o01033: self.i_RRC,
                               0o01041: self.i_TPR,
                               0o01042: self.i_TCF,
                               0o01043: self.i_TPC,
                               0o01051: self.i_HRB,
                               0o01052: self.i_HOF,
                               0o01061: self.i_HON,
                               0o01062: self.i_STB,
                               0o01071: self.i_SCF,
                               0o01072: self.i_IOS,
                               0o01101: self.i_IOT101,
                               0o01111: self.i_IOT111,
                               0o01131: self.i_IOT131,
                               0o01132: self.i_IOT132,
                               0o01134: self.i_IOT134,
                               0o01141: self.i_IOT141,
                               0o01161: self.i_IOF,
                               0o01162: self.i_ION,
                               0o01271: self.i_PPC,
                               0o01274: self.i_PSF,
             #                 0o03000: self.illegal RAL0
                               0o03001: self.i_RAL1,
                               0o03002: self.i_RAL2,
                               0o03003: self.i_RAL3,
             #                 0o03020: self.illegal RAR0,
                               0o03021: self.i_RAR1,
                               0o03022: self.i_RAR2,
                               0o03023: self.i_RAR3,
             #                 0o03040: self.illegal SAL0,
                               0o03041: self.i_SAL1,
                               0o03042: self.i_SAL2,
                               0o03043: self.i_SAL3,
             #                 0o03060: self.illegal SAR0,
                               0o03061: self.i_SAR1,
                               0o03062: self.i_SAR2,
                               0o03063: self.i_SAR3,
                               0o03100: self.i_DON}

        self.page02_decode = {0o002001: self.i_ASZ,
                              0o102001: self.i_ASN,
                              0o002002: self.i_ASP,
                              0o102002: self.i_ASM,
                              0o002004: self.i_LSZ,
                              0o102004: self.i_LSN,
                              0o002010: self.i_DSF,
                              0o102010: self.i_DSN,
                              0o002020: self.i_KSF,
                              0o102020: self.i_KSN,
                              0o002040: self.i_RSF,
                              0o102040: self.i_RSN,
                              0o002100: self.i_TSF,
                              0o102100: self.i_TSN,
                              0o002200: self.i_SSF,
                              0o102200: self.i_SSN,
                              0o002400: self.i_HSF,
                              0o102400: self.i_HSN}

        self.micro_opcodes = {0o100000: 'NOP',
                              0o100001: 'CLA',
                              0o100002: 'CMA',
                              0o100003: 'STA',
                              0o100004: 'IAC',
                              0o100005: 'COA',
                              0o100006: 'CIA',
                              0o100010: 'CLL',
                              0o100011: 'CAL',
                              0o100020: 'CML',
                              0o100030: 'STL',
                              0o100040: 'ODA',
                              0o100041: 'LDA'}

        self.micro_singles = {0o100001: 'CLA',
                              0o100002: 'CMA',
                              0o100004: 'IAC',
                              0o100010: 'CLL',
                              0o100020: 'CML',
                              0o100040: 'ODA'}


        self.running = False

    def set_dataswitches(self, value):
        """Set given value into the data switches."""

        self.DS = value

    def BLOCKADDR(self, address):
        """Get address WITHIN THE BLOCK."""

        return self.BlockBase | address

    def execute_one_instruction(self):
        """Execute one MAIN instruction, return # cycles and a trace string."""

        if not self.running:
            return (0, None)

        # get instruction word to execute, advance PC
        self.dot = self.PC
        instruction = self.memory.fetch(self.dot, False)
        self.BlockBase = self.PC & ADDRHIGHMASK
        self.PC = MASK_MEM(self.PC + 1)

        # get instruction opcode, indirect bit and address
        opcode = (instruction >> 11) & 0o17
        indirect = bool(instruction & 0o100000)
        address = (instruction & 0o3777)

        return self.main_decode.get(opcode, self.illegal)(indirect,
                                                          address,
                                                          instruction)

    def illegal(self, indirect, address, instruction):
        """Handle an illegal instruction."""

        if instruction:
            msg = ('Illegal instruction (%6.6o) at address %6.6o'
                   % (instruction, self.PC-1))
        else:
            msg = 'Illegal instruction at address %6.6o' % (PC-1)
        raise RuntimeError(msg)

    def page_00(self, indirect, address, instruction):
        if (instruction & 0o077700) == 0o00000:
            return self.microcode(instruction)
        elif (instruction & 0o077000) == 0o02000:
            return self.page02_decode.get(instruction, self.illegal)()

        return self.page_00_decode.get(instruction, self.illegal)(indirect,
                                                                  address,
                                                                  instruction)

    def i_LAW_LWC(self, indirect, address, instruction):
        tracestr = None
        if indirect:
            self.AC = (~address+1) & WORDMASK
            tracestr = trace.itrace(self.dot, 'LWC', False, address)
        else:
            self.AC = address
            tracestr = trace.itrace(self.dot, 'LAW', False, address)
        return (1, tracestr)

    def i_JMP(self, indirect, address, instruction):
        eff_address = self.memory.eff_address(address, indirect)
        self.PC = eff_address & PCMASK
        tracestr = trace.itrace(self.dot, 'JMP', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_DAC(self, indirect, address, instruction):
        eff_address = self.memory.eff_address(address, indirect)
        self.memory.put(self.AC, eff_address, False)
        tracestr = trace.itrace(self.dot, 'DAC', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_XAM(self, indirect, address, instruction):
        eff_address = self.memory.eff_address(address, indirect)
        tmp = self.memory.fetch(eff_address, False)
        self.memory.put(self.AC, eff_address, False)
        self.AC = tmp
        tracestr = trace.itrace(self.dot, 'XAM', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_ISZ(self, indirect, address, instruction):
        eff_address = self.memory.eff_address(address, indirect)
        value = (self.memory.fetch(eff_address, False) + 1) & WORDMASK
        self.memory.put(value, eff_address, False)
        if value == 0:
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'ISZ', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_JMS(self, indirect, address, instruction):
        eff_address = self.memory.eff_address(address, indirect)
        self.memory.put(self.PC, eff_address, False)
        self.PC = (eff_address + 1) & PCMASK
        tracestr = trace.itrace(self.dot, 'JMS', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_AND(self, indirect, address, instruction):
        self.AC &= self.memory.fetch(address, indirect)
        tracestr = trace.itrace(self.dot, 'AND', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_IOR(self, indirect, address, instruction):
        self.AC |= self.memory.fetch(address, indirect)
        tracestr = trace.itrace(self.dot, 'IOR', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_XOR(self, indirect, address, instruction):
        self.AC ^= self.memory.fetch(address, indirect)
        tracestr = trace.itrace(self.dot, 'XOR', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_LAC(self, indirect, address, instruction):
        self.AC = self.memory.fetch(address, indirect)
        tracestr = trace.itrace(self.dot, 'LAC', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_ADD(self, indirect, address, instruction):
        self.AC += self.memory.fetch(self.BLOCKADDR(address), indirect)
        if self.AC & OVERFLOWMASK:
            self.L = 0 if self.L else 1
        self.AC &= WORDMASK
        tracestr = trace.itrace(self.dot, 'ADD', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_SUB(self, indirect, address, instruction):
        addit = self.memory.fetch(self.BLOCKADDR(address), indirect)
        addit = (~addit + 1) & WORDMASK
        self.AC += addit
        if self.AC & OVERFLOWMASK:
            self.L = 0 if self.L else 1
        self.AC &= WORDMASK
        tracestr = trace.itrace(self.dot, 'SUB', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_SAM(self, indirect, address, instruction):
        samaddr = self.BLOCKADDR(address)
        if self.AC == self.memory.fetch(samaddr, indirect):
            self.PC = (self.PC + 1) & PCMASK
        tracestr = trace.itrace(self.dot, 'SAM', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def microcode(self, instruction):
        # T1
        if instruction & 0o01:
            self.AC = 0
        if instruction & 0o10:
            self.L = 0

        # T2
        if instruction & 0o02:
            self.AC = (~self.AC) & WORDMASK
        if instruction & 0o20:
            self.L = 0 if self.L else 1

        # T3
        if instruction & 0o04:
            self.AC += 1
            if self.AC & OVERFLOWMASK:
                self.L = 0 if self.L else 1
            self.AC &= WORDMASK
        if instruction & 0o40:
            self.AC |= self.DS

        # do some sort of trace
        combine = []
        opcode = self.micro_opcodes.get(instruction, None)
        if opcode:
            combine.append(opcode)

        if not combine:
            # nothing so far, we have HLT or unknown microcode
            if not instruction & 0o100000:
                # bit 0 is clear, it's HLT
                self.running = False
                combine.append('HLT')
            else:
                for (k, op) in self.micro_singles.items():
                    if instruction & k:
                        combine.append(op)

        tracestr = trace.itrace(self.dot, '+'.join(combine), False)
        return (1, tracestr)

    def i_DLA(self, indirect, address, instruction):
        self.displaycpu.DPC = self.AC
        tracestr = trace.itrace(self.dot, 'DLA')
        return (1, tracestr)

    def i_CTB(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'CTB')
        return (1, tracestr)

    def i_DOF(self, indirect, address, instruction):
        log('self.displaycpu=%s' % str(self.displaycpu))
        self.displaycpu.stop()
        tracestr = trace.itrace(self.dot, 'DOF')
        return (1, tracestr)

    def i_KRB(self, indirect, address, instruction):
        self.AC |= self.kbd.read()
        tracestr = trace.itrace(self.dot, 'KRB')
        return (1, tracestr)

    def i_KCF(self, indirect, address, instruction):
        self.kbd.clear()
        tracestr = trace.itrace(self.dot, 'KCF')
        return (1, tracestr)

    def i_KRC(self, indirect, address, instruction):
        self.AC |= self.kbd.read()
        self.kbd.clear()
        tracestr = trace.itrace(self.dot, 'KRC')
        return (1, tracestr)

    def i_RRB(self, indirect, address, instruction):
        self.AC |= self.ttyin.read()
        tracestr = trace.itrace(self.dot, 'RRB')
        return (1, tracestr)

    def i_RCF(self, indirect, address, instruction):
        self.ttyin.clear()
        tracestr = trace.itrace(self.dot, 'RCF')
        return (1, tracestr)

    def i_RRC(self, indirect, address, instruction):
        self.AC |= self.ttyin.read()
        self.ttyin.clear()
        tracestr = trace.itrace(self.dot, 'RRC')
        return (1, tracestr)

    def i_TPR(self, indirect, address, instruction):
        self.ttyout.write(self.AC & 0xff)
        tracestr = trace.itrace(self.dot, 'TPR')
        return (1, tracestr)

    def i_TCF(self, indirect, address, instruction):
        self.ttyout.clear()
        tracestr = trace.itrace(self.dot, 'TCF')
        return (1, tracestr)

    def i_TPC(self, indirect, address, instruction):
        self.ttyout.write(self.AC & 0xff)
        self.ttyout.clear()
        tracestr = trace.itrace(self.dot, 'TPC')
        return (1, tracestr)

    def i_HRB(self, indirect, address, instruction):
        self.AC |= self.ptrptp.read()
        tracestr = trace.itrace(self.dot, 'HRB')
        return (1, tracestr)

    def i_HOF(self, indirect, address, instruction):
        self.ptrptp.stop()
        tracestr = trace.itrace(self.dot, 'HOF')
        return (1, tracestr)

    def i_HON(self, indirect, address, instruction):
        self.ptrptp.start()
        tracestr = trace.itrace(self.dot, 'HON')
        return (1, tracestr)

    def i_STB(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'STB')
        return (1, tracestr)

    def i_SCF(self, indirect, address, instruction):
        self.Sync40Hz = 0
        tracestr = trace.itrace(self.dot, 'SCF')
        return (1, tracestr)

    def i_IOS(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOS')
        return (1, tracestr)

    def i_IOT101(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT101')
        return (1, tracestr)

    def i_IOT111(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT111')
        return (1, tracestr)

    def i_IOT131(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT131')
        return (1, tracestr)

    def i_IOT132(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT132')
        return (1, tracestr)

    def i_IOT134(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT134')
        return (1, tracestr)

    def i_IOT141(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOT141')
        return (1, tracestr)

    def i_IOF(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'IOF')
        return (1, tracestr)

    def i_ION(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'ION')
        return (1, tracestr)

    def i_PPC(self, indirect, address, instruction):
        self.ptrptp.punch(self.AC & 0xff)
        tracestr = trace.itrace(self.dot, 'PPC')
        return (1, tracestr)

    def i_PSF(self, indirect, address, instruction):
        if self.ptrptp.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'PSF')
        return (1, tracestr)

    def i_RAL1(self, indirect, address, instruction):
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAL', False, 1)
        return (1, tracestr)

    def i_RAL2(self, indirect, address, instruction):
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAL', False, 2)
        return (1, tracestr)

    def i_RAL3(self, indirect, address, instruction):
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC >> 15
        newac = (self.AC << 1) | self.L
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAL', False, 3)
        return (1, tracestr)

    def i_RAR1(self, indirect, address, instruction):
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAR', False, 1)
        return (1, tracestr)

    def i_RAR2(self, indirect, address, instruction):
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAR', False, 2)
        return (1, tracestr)

    def i_RAR3(self, indirect, address, instruction):
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        newl = self.AC & 1
        newac = (self.AC >> 1) | (self.L << 15)
        self.L = newl
        self.AC = newac & WORDMASK
        tracestr = trace.itrace(self.dot, 'RAR', False, 3)
        return (1, tracestr)

    def i_SAL1(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        value = self.AC & 0o37777
        self.AC = (value << 1) | high_bit
        tracestr = trace.itrace(self.dot, 'SAL', False, 1)
        return (1, tracestr)

    def i_SAL2(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        value = self.AC & 0o17777
        self.AC = (value << 2) | high_bit
        tracestr = trace.itrace(self.dot, 'SAL', False, 2)
        return (1, tracestr)

    def i_SAL3(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        value = self.AC & 0o07777
        self.AC = (value << 3) | high_bit
        tracestr = trace.itrace(self.dot, 'SAL', False, 3)
        return (1, tracestr)

    def i_SAR1(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        self.AC = (self.AC >> 1) | high_bit
        tracestr = trace.itrace(self.dot, 'SAR', False, 1)
        return (1, tracestr)

    def i_SAR2(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        self.AC = (self.AC >> 1) | high_bit
        self.AC = (self.AC >> 1) | high_bit
        tracestr = trace.itrace(self.dot, 'SAR', False, 2)
        return (1, tracestr)

    def i_SAR3(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        self.AC = (self.AC >> 1) | high_bit
        self.AC = (self.AC >> 1) | high_bit
        self.AC = (self.AC >> 1) | high_bit
        tracestr = trace.itrace(self.dot, 'SAR', False, 3)
        return (1, tracestr)

    def i_DON(self, indirect, address, instruction):
        self.display.clear()
        self.displaycpu.DRSindex = 0
        self.displaycpu.start()
        tracestr = trace.itrace(self.dot, 'DON')
        return (1, tracestr)

    def i_ASZ(self):
        if self.AC == 0:
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'ASZ')
        return (1, tracestr)

    def i_ASN(self):
        if self.AC != 0:
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'ASN')
        return (1, tracestr)

    def i_ASP(self):
        if not (self.AC & HIGHBITMASK):
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'ASP')
        return (1, tracestr)

    def i_ASM(self):
        if (self.AC & HIGHBITMASK):
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'ASM')
        return (1, tracestr)

    def i_LSZ(self):
        if self.L == 0:
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'LSZ')
        return (1, tracestr)

    def i_LSN(self):
        if self.L != 0:
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'LSN')
        return (1, tracestr)

    def i_DSF(self):
        if self.displaycpu.ison():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'DSF')
        return (1, tracestr)

    def i_DSN(self):
        if not self.displaycpu.ison():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'DSN')
        return (1, tracestr)

    def i_KSF(self):
        if self.kbd.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'KSF')
        return (1, tracestr)

    def i_KSN(self):
        if not self.kbd.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'KSN')
        return (1, tracestr)

    def i_RSF(self):
        if self.ttyin.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'RSF')
        return (1, tracestr)

    def i_RSN(self):
        if not self.ttyin.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'RSN')
        return (1, tracestr)

    def i_TSF(self):
        if self.ttyout.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'TSF')
        return (1, tracestr)

    def i_TSN(self):
        if not self.ttyout.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'TSN')
        return (1, tracestr)

    def i_SSF(self):
        if self.display.ready():	# skip if 40Hz sync on
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'SSF')
        return (1, tracestr)

    def i_SSN(self):
        if not self.display.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'SSN')
        return (1, tracestr)

    def i_HSF(self):
        if self.ptrptp.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'HSF')
        return (1, tracestr)

    def i_HSN(self):
        if not self.ptrptp.ready():
            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'HSN')
        return (1, tracestr)

