#!/usr/bin/python

"""
The Imlac main CPU.
"""


import sys

from Globals import *
import DisplayCPU
import Memory
import Ptr
import Ptp
import TtyIn
import TtyOut
import Kbd
import Trace


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

# decode dictionaries (initialized in init())
main_decode = None
page_00_decode = None
page02_decode = None
micro_opcodes = None
micro_singles = None

# module-level state variables
running = False


def init():
    global running, main_decode, page_00_decode, page02_decode, micro_opcodes
    global micro_singles

    # main dispatch dictionary for decoding opcodes in bits 1-4
    main_decode = {000: page_00,	# secondary decode
                   001: i_LAW_LWC,
                   002: i_JMP,
    #              003: illegal,
                   004: i_DAC,
                   005: i_XAM,
                   006: i_ISZ,
                   007: i_JMS,
    #              010: illegal
                   011: i_AND,
                   012: i_IOR,
                   013: i_XOR,
                   014: i_LAC,
                   015: i_ADD,
                   016: i_SUB,
                   017: i_SAM}
    
    # page_00 dispatch dictionary for decoding opcodes
    # HLT may be handled specially
    page_00_decode = {001003: i_DLA,
                      001011: i_CTB,
                      001012: i_DOF,
                      001021: i_KRB,
                      001022: i_KCF,
                      001023: i_KRC,
                      001031: i_RRB,
                      001032: i_RCF,
                      001033: i_RRC,
                      001041: i_TPR,
                      001042: i_TCF,
                      001043: i_TPC,
                      001051: i_HRB,
                      001052: i_HOF,
                      001061: i_HON,
                      001062: i_STB,
                      001071: i_SCF,
                      001072: i_IOS,
                      001101: i_IOT101,
                      001111: i_IOT111,
                      001131: i_IOT131,
                      001132: i_IOT132,
                      001134: i_IOT134,
                      001141: i_IOT141,
                      001161: i_IOF,
                      001162: i_ION,
                      001271: i_PUN,
                      001274: i_PSF,
    #                 003000: illegal RAL0
                      003001: i_RAL1,
                      003002: i_RAL2,
                      003003: i_RAL3,
    #                 003020: illegal RAR0,
                      003021: i_RAR1,
                      003022: i_RAR2,
                      003023: i_RAR3,
    #                 003040: illegal SAL0,
                      003041: i_SAL1,
                      003042: i_SAL2,
                      003043: i_SAL3,
    #                 003060: illegal SAR0,
                      003061: i_SAR1,
                      003062: i_SAR2,
                      003063: i_SAR3,
                      003100: i_DON}
    
    page02_decode = {0002001: i_ASZ,
                     0102001: i_ASN,
                     0002002: i_ASP,
                     0102002: i_ASM,
                     0002004: i_LSZ,
                     0102004: i_LSN,
                     0002010: i_DSF,
                     0102010: i_DSN,
                     0002020: i_KSF,
                     0102020: i_KSN,
                     0002040: i_RSF,
                     0102040: i_RSN,
                     0002100: i_TSF,
                     0102100: i_TSN,
                     0002200: i_SSF,
                     0102200: i_SSN,
                     0002400: i_HSF,
                     0102400: i_HSN}

    micro_opcodes = {0100000: 'NOP',
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

    micro_singles = {0100001: 'CLA',
                     0100002: 'CMA',
                     0100004: 'IAC',
                     0100010: 'CLL',
                     0100020: 'CML',
                     0100040: 'ODA'}


    running = False

def EFFADDR(address):
    return BlockBase | address

def execute_one_instruction():
    """Execute one MAIN instruction, return # cycles used"""

    global PC, BlockBase

    if not running:
        return 0

    # get instruction word to execute, advance PC
    instruction = Memory.get(PC, False)
    BlockBase = PC & ADDRHIGHMASK
    PC = MASK_MEM(PC + 1)

    # get instruction opcode, indirect bit and address
    opcode = (instruction >> 11) & 017
    indirect = (instruction & 0100000)
    address = (instruction & 03777)

    return main_decode.get(opcode, illegal)(indirect, address, instruction)

def illegal(indirect, address, instruction):
    if instruction:
        msg = ('Illegal instruction (%6.6o) at address %6.6o'
               % (instruction, PC-1))
    else:
        msg = 'Illegal instruction at address %6.6o' % (PC-1)
    raise RuntimeError(msg)

def page_00(indirect, address, instruction):
    if (instruction & 0077700) == 000000:
        return microcode(instruction)
    elif (instruction & 0077000) == 002000:
        return page02_decode.get(instruction, illegal)()

    return page_00_decode.get(instruction, illegal)(indirect,
                                                    address, instruction)

def i_LAW_LWC(indirect, address, instruction):
    global AC

    if indirect:
        AC = ((~address) + 1) & WORDMASK
        Trace.itrace('LWC', False, address)
    else:
        AC = address
        Trace.itrace('LAW', False, address)
    return 1

def i_JMP(indirect, address, instruction):
    global PC

    jmpaddr = EFFADDR(address)
    if indirect:
        jmpaddr = Memory.get(jmpaddr, False)
    PC = jmpaddr & PCMASK
    Trace.itrace('JMP', indirect, address)
    return 3 if indirect else 2

def i_DAC(indirect, address, instruction):
    address = EFFADDR(address)
    Memory.put(AC, address, indirect)
    Trace.itrace('DAC', indirect, address)
    return 3 if indirect else 2

def i_XAM(indirect, address, instruction):
    global AC

    if indirect:
        address = Memory.get(address, False)
    tmp = Memory.get(address, False)
    Memory.put(AC, address, False)
    AC = tmp
    Trace.itrace('XAM', indirect, address)
    return 3 if indirect else 2

def i_ISZ(indirect, address, instruction):
    global PC

    value = (Memory.get(address, indirect) + 1) & WORDMASK
    Memory.put(value, address, indirect)
    if value == 0:
        PC = (PC + 1) & WORDMASK
    Trace.itrace('ISZ', indirect, address)
    return 3 if indirect else 2

def i_JMS(indirect, address, instruction):
    global PC

    jmsaddr = EFFADDR(address)
    if indirect:
        jmsaddr = Memory.get(jmsaddr, False)
    Memory.put(PC, jmsaddr, False)
    PC = (jmsaddr + 1) & PCMASK
    Trace.itrace('JMS', indirect, address)
    return 3 if indirect else 2

def i_AND(indirect, address, instruction):
    global AC

    AC &= Memory.get(address, indirect)
    Trace.itrace('AND', indirect, address)
    return 3 if indirect else 2

def i_IOR(indirect, address, instruction):
    global AC

    AC |= Memory.get(address, indirect)
    Trace.itrace('IOR', indirect, address)
    return 3 if indirect else 2

def i_XOR(indirect, address, instruction):
    global AC

    AC ^= Memory.get(address, indirect)
    Trace.itrace('XOR', indirect, address)
    return 3 if indirect else 2

def i_LAC(indirect, address, instruction):
    global AC

    AC = Memory.get(address, indirect)
    Trace.itrace('LAC', indirect, address)
    return 3 if indirect else 2

def i_ADD(indirect, address, instruction):
    global AC, L

    effaddress = EFFADDR(address)
    AC += Memory.get(address, indirect)
    if AC & OVERFLOWMASK:
        L = not L
        AC &= WORDMASK
    Trace.itrace('ADD', indirect, address)
    return 3 if indirect else 2

def i_SUB(indirect, address, instruction):
    global AC, L

    effaddr = EFFADDR(address)
    AC -= Memory.get(address, indirect)
    if AC & OVERFLOWMASK:
        L = not L
        AC &= WORDMASK
    Trace.itrace('SUB', indirect, address)
    return 3 if indirect else 2

def i_SAM(indirect, address, instruction):
    global PC

    samaddr = EFFADDR(address)
    if indirect:
        samaddr = Memory.get(samaddr, False)
    if AC == Memory.get(samaddr, False):
        PC = (PC + 1) & PCMASK
    Trace.itrace('SAM', indirect, address)
    return 3 if indirect else 2

def microcode(instruction):
    global AC, L, PC, running

    # T1
    if (instruction & 001):
        AC = 0
    if (instruction & 010):
        L = 0

    # T2
    if (instruction & 002):
        AC = (~AC) & WORDMASK
    if (instruction & 020):
        L = (~L) & 01

    # T3
    if (instruction & 004):
        newac = AC + 1
        if newac & OVERFLOWMASK:
            L = (~L) & 01
        AC = newac & WORDMASK
    if (instruction & 040):
        AC |= DS
        L = (~L) & 1

    # do some sort of trace
    combine = []
    opcode = micro_opcodes.get(instruction, None)
    if opcode:
        combine.append(opcode)

    if not combine:
        # nothing so far, we have HLT or unknown microcode
        if not instruction & 0100000:
            # bit 0 is clear, it's HLT
            running = False
            combine.append('HLT')
        else:
            for (k, op) in micro_singles.items():
                if instruction & k:
                    combine.append(op)

    Trace.itrace('+'.join(combine), False)
    return 1

def i_DLA(indirect, address, instruction):
    DisplayCPU.DPC = AC
    Trace.itrace('DLA')
    return 1

def i_CTB(indirect, address, instruction):
    Trace.itrace('CTB')
    return 1

def i_DOF(indirect, address, instruction):
    DisplayCPU.stop()
    Trace.itrace('DOF')
    return 1

def i_KRB(indirect, address, instruction):
    global AC

    AC |= Kbd.read()
    Trace.itrace('KRB')
    return 1

def i_KCF(indirect, address, instruction):
    Kbd.clear()
    Trace.itrace('KCF')
    return 1

def i_KRC(indirect, address, instruction):
    global AC

    AC |= Kbd.read()
    Kbd.clear()
    Trace.itrace('KRC')
    return 1

def i_RRB(indirect, address, instruction):
    global AC

    AC |= TtyIn.read()
    Trace.itrace('RRB')
    return 1

def i_RCF(indirect, address, instruction):
    TtyIn.clear()
    Trace.itrace('RCF')
    return 1

def i_RRC(indirect, address, instruction):
    global AC

    AC |= TtyIn.read()
    TtyIn.clear()
    Trace.itrace('RRC')
    return 1

def i_TPR(indirect, address, instruction):
    TtyOut.write(AC & 0xff)
    Trace.itrace('TPR')
    return 1

def i_TCF(indirect, address, instruction):
    TtyOut.clear()
    Trace.itrace('TCF')
    return 1

def i_TPC(indirect, address, instruction):
    TtyOut.write(AC & 0xff)
    TtyOut.clear()
    Trace.itrace('TPC')
    return 1

def i_HRB(indirect, address, instruction):
    global AC

    AC |= Ptr.read()
    Trace.itrace('HRB')
    return 1

def i_HOF(indirect, address, instruction):
    Ptr.stop()
    Trace.itrace('HOF')
    return 1

def i_HON(indirect, address, instruction):
    Ptr.start()
    Trace.itrace('HON')
    return 1

def i_STB(indirect, address, instruction):
    Trace.itrace('STB')
    return 1

def i_SCF(indirect, address, instruction):
    global Sync40Hz

    Sync40Hz = 0
    Trace.itrace('SCF')
    return 1

def i_IOS(indirect, address, instruction):
    Trace.itrace('IOS')
    return 1

def i_IOT101(indirect, address, instruction):
    Trace.itrace('IOT101')
    return 1

def i_IOT111(indirect, address, instruction):
    Trace.itrace('IOT111')
    return 1

def i_IOT131(indirect, address, instruction):
    Trace.itrace('IOT131')
    return 1

def i_IOT132(indirect, address, instruction):
    Trace.itrace('IOT132')
    return 1

def i_IOT134(indirect, address, instruction):
    Trace.itrace('IOT134')
    return 1

def i_IOT141(indirect, address, instruction):
    Trace.itrace('IOT141')
    return 1

def i_IOF(indirect, address, instruction):
    Trace.itrace('IOF')
    return 1

def i_ION(indirect, address, instruction):
    Trace.itrace('ION')
    return 1

def i_PUN(indirect, address, instruction):
    Ptp.write(PC & 0xff)
    Trace.itrace('PUN')
    return 1

def i_PSF(indirect, address, instruction):
    global PC

    if Ptp.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('PSF')
    return 1

def i_RAL1(indirect, address, instruction):
    global AC, L

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAL', False, 1)
    return 1

def i_RAL2(indirect, address, instruction):
    global AC, L

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAL', False, 2)
    return 1

def i_RAL3(indirect, address, instruction):
    global AC, L

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    newl = AC >> 15
    newac = (AC << 1) | L
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAL', False, 3)
    return 1

def i_RAR1(indirect, address, instruction):
    global AC, L

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAR', False, 1)
    return 1

def i_RAR2(indirect, address, instruction):
    global AC, L

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAR', False, 2)
    return 1

def i_RAR3(indirect, address, instruction):
    global AC, L

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    newl = AC & 1
    newac = (AC >> 1) | (L << 15)
    L = newl
    AC = newac & WORDMASK

    Trace.itrace('RAR', False, 3)
    return 1

def i_SAL1(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    value = AC & 037777
    AC = (value << 1) | high_bit
    Trace.itrace('SAL', False, 1)
    return 1

def i_SAL2(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    value = AC & 017777
    AC = (value << 2) | high_bit
    Trace.itrace('SAL', False, 2)
    return 1

def i_SAL3(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    value = AC & 007777
    AC = (value << 3) | high_bit
    Trace.itrace('SAL', False, 3)
    return 1

def i_SAR1(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    AC = (AC >> 1) | high_bit
    Trace.itrace('SAR', False, 1)
    return 1

def i_SAR2(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    AC = (AC >> 1) | high_bit
    AC = (AC >> 1) | high_bit
    Trace.itrace('SAR', False, 2)
    return 1

def i_SAR3(indirect, address, instruction):
    global AC

    high_bit = AC & HIGHBITMASK
    AC = (AC >> 1) | high_bit
    AC = (AC >> 1) | high_bit
    AC = (AC >> 1) | high_bit
    Trace.itrace('SAR', False, 3)
    return 1

def i_DON(indirect, address, instruction):
    DisplayCPU.DRSindex = 0
    DisplayCPU.start()
    Trace.itrace('DON')
    return 1

def i_ASZ():
    global PC

    if AC == 0:
        PC = (PC + 1) & WORDMASK
    Trace.itrace('ASZ')
    return 1

def i_ASN():
    global PC

    if AC != 0:
        PC = (PC + 1) & WORDMASK
    Trace.itrace('ASN')
    return 1

def i_ASP():
    global PC

    if not (AC & HIGHBITMASK):
        PC = (PC + 1) & WORDMASK
    Trace.itrace('ASP')
    return 1

def i_ASM():
    global PC

    if (AC & HIGHBITMASK):
        PC = (PC + 1) & WORDMASK
    Trace.itrace('ASM')
    return 1

def i_LSZ():
    global PC

    if L == 0:
        PC = (PC + 1) & WORDMASK
    Trace.itrace('LSZ')
    return 1

def i_LSN():
    global PC

    if L != 0:
        PC = (PC + 1) & WORDMASK
    Trace.itrace('LSN')
    return 1

def i_DSF():
    global PC

    if DisplayCPU.ison():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('DSF')
    return 1

def i_DSN():
    global PC

    if not DisplayCPU.ison():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('DSN')
    return 1

def i_KSF():
    global PC

    if Kbd.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('KSF')
    return 1

def i_KSN():
    global PC

    if not Kbd.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('KSN')
    return 1

def i_RSF():
    global PC

    if TtyIn.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('RSF')
    return 1

def i_RSN():
    global PC

    if not TtyIn.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('RSN')
    return 1

def i_TSF():
    global PC

    if TtyOut.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('TSF')
    return 1

def i_TSN():
    global PC

    if not TtyOut.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('TSN')
    return 1

def i_SSF():
    global PC

    if Display.ready():	# skip if 40Hz sync on
        PC = (PC + 1) & WORDMASK
    Trace.itrace('SSF')
    return 1

def i_SSN():
    global PC

    if not Display.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('SSN')
    return 1

def i_HSF():
    global PC

    if Ptr.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('HSF')
    return 1

def i_HSN():
    global PC

    if not Ptr.ready():
        PC = (PC + 1) & WORDMASK
    Trace.itrace('HSN')
    return 1

