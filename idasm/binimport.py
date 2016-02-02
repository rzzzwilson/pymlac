#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import an imlac binary file.
"""

import sys
import getopt
import struct
import wx
import mem
import disasmdata


# address where next word will be loaded into memory
Dot = 0

# dictionary of memory 'chunks'
# {<base_address>: [word1, word2, ...], ...}
Memory = {}

# size of memory configured
MemSize = 04000

# size of block loader
LoaderSize = 0100


def doblockloader(f, word, mymem):
    """Read block loader into high memory.

    f      file handle to read from
    word   the word we have already read
    mymem  Mem() object to store loader in
    """

    ldaddr = MemSize - LoaderSize
    numwords = LoaderSize - 1     # have already read one word in
    mymem.add(ldaddr, word)
    while numwords > 0:
        word = readword(f)
        mymem.add(ldaddr, word)
        ldaddr += 1
        numwords = numwords - 1

def calc_checksum(csum, word):
    """Calculate new checksum from word value.

    csum    old checksum value
    word  new word to include in checksum

    Returns the new checksum value.
    """

    csum += word
#    if csum & 0xffff:
#        # add got overflow
#        csum = (csum & 0xffff) + 1

    return csum & 0xffff


def dobody(f, mymem):
    """Read all of file after block loader.

    f      input file handle
    mymem  the mem.Mem() dict to store data in

    Returns an updated mem.Mem() object containing the input code.
    """

    numwords = skipzeros(f)
    while True:
        # negative load address is end-of-file
        ldaddr = readword(f)
        if ldaddr & 0x8000:
            break

        # read data block, calculating checksum
        csum = 0
        #csum = ldaddr
        while numwords > 0:
            word = readword(f)
            csum += word
            csum &= 0xffff
            mymem.add(ldaddr, word)
            (op, fld) = disasmdata.disasmdata(word)
            mymem.putOp(ldaddr, op)
            mymem.putFld(ldaddr, fld)
            ldaddr += 1
            numwords -= 1
        csum &= 0xffff
        checksum = readword(f)
        if csum != checksum:
            #wx.MessageBox('Checksum error', 'Error', wx.OK | wx.ICON_ERROR)
            wx.MessageBox('Checksum error', 'Warning', wx.OK | wx.ICON_WARNING)
#            return None
        numwords = skipzeros(f)

    return mymem

def ptpimport(file):
    global Dot

    try:
        f = open(file, "rb")
    except IOError as e:
        print e
        return 3

    # create Mem() object to store data
    mymem = mem.Mem()

    Dot = 0

    # find and read the block loader
    byte = skipzeros(f)
    word = (byte << 8) + readbyte(f)
    doblockloader(f, word, mymem)

    # now read all the data blocks
    mymem = dobody(f, mymem)

    return mymem

def readbyte(f):
    global Dot

    try:
        byte = f.read(1)
    except IOError as e:
        print e
        sys.exit(10)
    except EOFError as e:
        print e
        sys.exit(11)
    Dot += 1
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
    themem = ptpimport('40tp_simpleDisplay.ptp')
    if themem is None:
        print('Error reading input file.')
        sys.exit(10)
    print('str(dir(themem))=%s' % str(dir(themem)))

    addrlist = themem.keys()
    addrlist.sort()
    for addr in addrlist:
        (word, cycle, type, lab, ref) = mymem[addr]
        print "%s %s: %05o" % (addr, type, word)
