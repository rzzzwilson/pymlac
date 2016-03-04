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

        self.memory = memory
        self.display = display
        self.displaycpu = displaycpu
        self.kbd = kbd
        self.ttyin = ttyin
        self.ttyout = ttyout
        self.ptrptp = ptrptp

        # main dispatch dictionary for decoding opcodes in bits 1-4
        self.main_decode = {000: self.page_00,	# secondary decode
                            001: self.i_LAW_LWC,
                            002: self.i_JMP,
        #                   003: self.illegal,
                            004: self.i_DAC,
                            005: self.i_XAM,
                            006: self.i_ISZ,
                            007: self.i_JMS,
        #                   010: self.illegal
                            011: self.i_AND,
                            012: self.i_IOR,
                            013: self.i_XOR,
                            014: self.i_LAC,
                            015: self.i_ADD,
                            016: self.i_SUB,
                            017: self.i_SAM}

        # page_00 dispatch dictionary for decoding opcodes
        # HLT may be handled specially
        self.page_00_decode = {001003: self.i_DLA,
                               001011: self.i_CTB,
                               001012: self.i_DOF,
                               001021: self.i_KRB,
                               001022: self.i_KCF,
                               001023: self.i_KRC,
                               001031: self.i_RRB,
                               001032: self.i_RCF,
                               001033: self.i_RRC,
                               001041: self.i_TPR,
                               001042: self.i_TCF,
                               001043: self.i_TPC,
                               001051: self.i_HRB,
                               001052: self.i_HOF,
                               001061: self.i_HON,
                               001062: self.i_STB,
                               001071: self.i_SCF,
                               001072: self.i_IOS,
                               001101: self.i_IOT101,
                               001111: self.i_IOT111,
                               001131: self.i_IOT131,
                               001132: self.i_IOT132,
                               001134: self.i_IOT134,
                               001141: self.i_IOT141,
                               001161: self.i_IOF,
                               001162: self.i_ION,
                               001271: self.i_PPC,
                               001274: self.i_PSF,
             #                 003000: self.illegal RAL0
                               003001: self.i_RAL1,
                               003002: self.i_RAL2,
                               003003: self.i_RAL3,
             #                 003020: self.illegal RAR0,
                               003021: self.i_RAR1,
                               003022: self.i_RAR2,
                               003023: self.i_RAR3,
             #                 003040: self.illegal SAL0,
                               003041: self.i_SAL1,
                               003042: self.i_SAL2,
                               003043: self.i_SAL3,
             #                 003060: self.illegal SAR0,
                               003061: self.i_SAR1,
                               003062: self.i_SAR2,
                               003063: self.i_SAR3,
                               003100: self.i_DON}

        self.page02_decode = {0002001: self.i_ASZ,
                              0102001: self.i_ASN,
                              0002002: self.i_ASP,
                              0102002: self.i_ASM,
                              0002004: self.i_LSZ,
                              0102004: self.i_LSN,
                              0002010: self.i_DSF,
                              0102010: self.i_DSN,
                              0002020: self.i_KSF,
                              0102020: self.i_KSN,
                              0002040: self.i_RSF,
                              0102040: self.i_RSN,
                              0002100: self.i_TSF,
                              0102100: self.i_TSN,
                              0002200: self.i_SSF,
                              0102200: self.i_SSN,
                              0002400: self.i_HSF,
                              0102400: self.i_HSN}

        self.micro_opcodes = {0100000: 'NOP',
                              0100001: 'CLA',
                              0100002: 'CMA',
                              0100003: 'STA',
                              0100004: 'IAC',
                              0100005: 'COA',
                              0100006: 'CIA',
                              0100010: 'CLL',
                              0100011: 'CAL',
                              0100020: 'CML',
                              0100030: 'STL',
                              0100040: 'ODA',
                              0100041: 'LDA'}

        self.micro_singles = {0100001: 'CLA',
                              0100002: 'CMA',
                              0100004: 'IAC',
                              0100010: 'CLL',
                              0100020: 'CML',
                              0100040: 'ODA'}


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
        opcode = (instruction >> 11) & 017
        indirect = bool(instruction & 0100000)
        address = (instruction & 03777)

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
        if (instruction & 0077700) == 000000:
            return self.microcode(instruction)
        elif (instruction & 0077000) == 002000:
            return self.page02_decode.get(instruction, self.illegal)()

        return self.page_00_decode.get(instruction, self.illegal)(indirect,
                                                                  address,
                                                                  instruction)

    def i_LAW_LWC(self, indirect, address, instruction):
        tracestr = None
        if indirect:
            self.AC = ~address & WORDMASK
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
        log('DAC: %s' % tracestr)
        log('DAC: storing %06o at address %06o' % (self.AC, eff_address))
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
            self.L = (~self.L) & 01
        self.AC &= WORDMASK
        tracestr = trace.itrace(self.dot, 'ADD', indirect, address)
        return (3, tracestr) if indirect else (2, tracestr)

    def i_SUB(self, indirect, address, instruction):
        addit = self.memory.fetch(self.BLOCKADDR(address), indirect)
        addit = (~addit + 1) & WORDMASK
        self.AC += addit
        if self.AC & OVERFLOWMASK:
            self.L = ~self.L
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
        if instruction & 001:
            self.AC = 0
        if instruction & 010:
            self.L = 0

        # T2
        if instruction & 002:
            self.AC = (~self.AC) & WORDMASK
        if instruction & 020:
            self.L = (~self.L) & 01

        # T3
        if instruction & 004:
            self.AC += 1
            if self.AC & OVERFLOWMASK:
                self.L = (~self.L) & 1
            self.AC &= WORDMASK
        if instruction & 040:
            self.AC |= self.DS

        # do some sort of trace
        combine = []
        opcode = self.micro_opcodes.get(instruction, None)
        if opcode:
            combine.append(opcode)

        if not combine:
            # nothing so far, we have HLT or unknown microcode
            if not instruction & 0100000:
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
        #self.displaycpu.DPC = self.AC
        tracestr = trace.itrace(self.dot, 'DLA_X')
        return (1, tracestr)

    def i_CTB(self, indirect, address, instruction):
        tracestr = trace.itrace(self.dot, 'CTB')
        return (1, tracestr)

    def i_DOF(self, indirect, address, instruction):
        #self.displaycpu.stop()
        tracestr = trace.itrace(self.dot, 'DOF_X')
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
        value = self.AC & 037777
        self.AC = (value << 1) | high_bit
        tracestr = trace.itrace(self.dot, 'SAL', False, 1)
        return (1, tracestr)

    def i_SAL2(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        value = self.AC & 017777
        self.AC = (value << 2) | high_bit
        tracestr = trace.itrace(self.dot, 'SAL', False, 2)
        return (1, tracestr)

    def i_SAL3(self, indirect, address, instruction):
        high_bit = self.AC & HIGHBITMASK
        value = self.AC & 007777
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
        #self.displaycpu.DRSindex = 0
        #self.displaycpu.start()
        tracestr = trace.itrace(self.dot, 'DON_X')
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
#        if self.displaycpu.ison():
#            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'DSF_X')
        return (1, tracestr)

    def i_DSN(self):
#        if not self.displaycpu.ison():
#            self.PC = (self.PC + 1) & WORDMASK
        tracestr = trace.itrace(self.dot, 'DSN_X')
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

