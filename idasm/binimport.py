#!/usr/bin/env python

"""
Import an imlac binary file
"""

import sys
import getopt
import struct
import mem
import disasmdata


offset = 0

def doblockloader(f, word):
    ldaddr = 0177700
    numwords = 0100
    while numwords > 0:
        word = readword(f)
        numwords = numwords - 1
        ldaddr = ldaddr + 1


def dobody(f, count):
    mymem = mem.Mem()

    numwords = count
    while True:
        ldaddr = readword(f)
        if ldaddr & 0x8000:
            break
        csum = 0
        while numwords > 0:
            word = readword(f)
            csum += word
            if csum > 0xffff:
                csum += 1
            csum = csum & 0xffff
            mymem.add(ldaddr, word)
            (op, fld) = disasmdata.disasmdata(word)
            mymem.putOp(ldaddr, op)
            mymem.putFld(ldaddr, fld)
            ldaddr += 1
            numwords -= 1
        checksum = readword(f)
        if csum != checksum:
            print "Checksum error"
            #sys.exit(20)
        numwords = skipzeros(f)
    return mymem


def ptpimport(file):
    global offset

    try:
        f = open(file, "rb")
    except IOError, e:
        print e
        return 3

    offset = 0

    byte = skipzeros(f)
    word = (byte << 8) + readbyte(f)
    doblockloader(f, word)

    count = skipzeros(f)
    mymem = dobody(f, count)

    return mymem


def readbyte(f):
    global offset
    try:
        byte = f.read(1)
    except IOError, e:
        print e
        sys.exit(10)
    except EOFError, e:
        print e
        sys.exit(11)
    offset += 1
    if len(byte) > 0:
        val = struct.unpack("B", byte)
        return val[0]
    else:
        return 0


def readword(f):
    return (readbyte(f) << 8) + readbyte(f)


def skipzeros(f):
    while True:
        val = readbyte(f)
        if val > 0:
            return val


if __name__ == "__main__":
    themem = ptpimport("keybrd.ptp")

    addrlist = themem.keys()
    addrlist.sort()
    for addr in addrlist:
        (word, cycle, type, lab, ref) = mymem[addr]
        print "%s %s: %05o" % (addr, type, word)
