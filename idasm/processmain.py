#!/usr/bin/env python

"""
Process main instructions from a start address.
"""


import mem
import disasmm


mainQ = []


def dequeMain():
    result = None
    if len(mainQ) > 0:
        result = mainQ[0]
        del mainQ[0]
    return result

def effAddress(addr, offset):
    return (addr & 0174000) + offset

def enqueMain(address):
    mainQ.append(address)

def getTargetAddress(code):
    return code & 03777

def isHLT(code):
    opcode = code & 0177700
    return opcode == 0000000

def isISZ(code):
    opcode = code & 0174000
    return opcode == 0030000 or opcode == 0130000

def isJMP(code):
    opcode = code & 0174000
    return opcode == 0010000 or opcode == 0110000

def isJMS(code):
    opcode = code & 0174000
    return opcode == 0034000 or opcode == 0134000

def isMemRef(code):
    opcode = code & 0174000
    if opcode == 0020000 or opcode == 0120000: return True
    if opcode == 0024000 or opcode == 0124000: return True
    if opcode == 0044000 or opcode == 0144000: return True
    if opcode == 0050000 or opcode == 0150000: return True
    if opcode == 0054000 or opcode == 0154000: return True
    if opcode == 0060000 or opcode == 0160000: return True
    if opcode == 0064000 or opcode == 0164000: return True
    if opcode == 0070000 or opcode == 0170000: return True
    if opcode == 0074000 or opcode == 0174000: return True
    return False

def isSAM(code):
    opcode = code & 0174000
    return opcode == 0074000 or opcode == 0174000

def isSkip(code):
    opcode = code & 0077777
    if opcode in [0002001, 0002002, 0002004, 0002010, 0002020,
                  0002040, 0002100, 0002200, 0002400]:
        return True
    return False

def process(mem, addrlist, newcycle):
    for addr in addrlist:
        enqueMain(addr)
    while len(mainQ) > 0:
        address = dequeMain()
        while True:
            if mem.getCycle(address) == newcycle:   # seen it already
                break
            mem.putCycle(address, newcycle)
            code = mem.getCode(address)
            if mem.getRef(address):
                mem.decLab(getTargetAddress(code))
            (op, fld) = disasmm.disasmm(code)
            mem.putOp(address, op)
            mem.putFld(address, fld)
            if isJMP(code):
                memref = effAddress(address, getTargetAddress(code))
                mem.setRef(address)
                mem.incLab(memref)
                enqueMain(memref)
                break
            elif isJMS(code):
                memref = effAddress(address, getTargetAddress(code))
                mem.setRef(address)
                mem.incLab(memref)
                enqueMain(memref+1)
            elif isISZ(code) or isSAM(code):
                memref = effAddress(address, getTargetAddress(code))
                mem.setRef(address)
                mem.incLab(memref)
                enqueMain(address+2)
            elif isMemRef(code):
                memref = effAddress(address, getTargetAddress(code))
                mem.setRef(address)
                mem.incLab(memref)
            elif isSkip(code):
                enqueMain(address+2)
            elif isHLT(code):
                break
            address = address + 1
