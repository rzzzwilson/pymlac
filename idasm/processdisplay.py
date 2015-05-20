#!/usr/bin/env python

"""
This module takes a memory dictionary of the form:

    { <memstr>: ( <type>, <wordvalue> ), ...}

and a start address and returns a processed dictionary, where the <type>
is changed to one of "main", "mainref", "disp", "dispref" or "ref".
"""


import mem
import disasmd


dispQ = []

def dequeDisp():
    result = None
    if len(dispQ) > 0:
        result = dispQ[0]
        del dispQ[0]
    return result

def effAddress(addr, offset):
    return (addr & 0174000) + offset

def enqueDisp(address):
    dispQ.append(address)

def getTargetAddress(code):
    return code & 07777

def isDHLT(code):
    return code == 0000000

def isDEIM(code):
    opcode = code & 0070000
    return opcode == 0030000

def isDEIMExit(code):
    hibyte = (code >> 8) & 0377
    lobyte = code & 0377
    return isDEIMExitByte(hibyte) or isDEIMExitByte(lobyte)

def isDEIMReturn(code):
    hibyte = (code >> 8) & 0377
    lobyte = code & 0377
    return isDEIMReturnByte(hibyte) or isDEIMReturnByte(lobyte)

def isDEIMExitByte(byte):
    return (byte & 0300) == 0100

def isDEIMReturnByte(byte):
    return (byte & 0240) == 0040

def isDJMP(code):
    opcode = code & 0070000
    return opcode == 0060000

def isDJMS(code):
    opcode = code & 0070000
    return opcode == 0050000

def isDRJM(code):
    return code == 0004040

def process(mem, addrlist, newcycle):
    mode = "normal"
    for addr in addrlist:
        enqueDisp(addr)
    while len(dispQ) > 0:
        address = dequeDisp()
        while True:
            if mem.getCycle(address) == newcycle:   # seen it already
                break
            mem.putCycle(address, newcycle)
            code = mem.getCode(address)
            (op, fld) = disasmd.disasmd(code)
            mem.putOp(address, op)
            mem.putFld(address, fld)
            if mode == "deim":
                if isDEIMExit(code):
                    mode = "normal"
                if isDEIMReturn(code):
                    break
            else:
                if mem.getRef(address):
                    mem.decLab(getTargetAddress(code))
                if isDJMP(code):
                    memref = effAddress(address, getTargetAddress(code))
                    mem.setRef(address)
                    mem.incLab(memref)
                    enqueDisp(memref)
                    break
                elif isDRJM(code):
                    break
                elif isDJMS(code):
                    memref = effAddress(address, getTargetAddress(code))
                    mem.setRef(address)
                    mem.incLab(memref)
                    enqueDisp(memref)
                elif isDEIM(code):
                    mode = "deim"
                elif isDHLT(code):
                    break
            address = address + 1
