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


def pyword(word):
    """Convert a 16bit value to a real python integer.

    That is, convert 0xFFFF to -1.
    """

    byte = (word >> 8) & 0xff
    byte2 = word & 0xff
    bstr = chr(byte) + chr(byte2)
    return struct.unpack(">h", bstr)[0]


def dobody(f, mymem):
    """Read all of file after block loader.

    f      input file handle
    mymem  the mem.Mem() dict to store data in

    Returns an updated mem.Mem() object containing the input code
    and a start address:
        (mem, start, ac)
    If a start address is not specified, 'start' and 'ac' are both None.

    If there was a checksum error, just return None.
    """

    start_address = None

    while True:
        # negative load address is end-of-file
        ldaddr = readword(f)
        print('read: ldaddr=%06o' % ldaddr)
        print('ldaddr=%s' % str(ldaddr))
        if ldaddr & 0x8000:
            print('End load: ldaddr=%06o' % ldaddr)
            break

        # read data block, calculating checksum
        csum = ldaddr                           # start checksum with base address
        print('BLOCK: ldaddr=%06o, csum=%06o' % (ldaddr, csum))
        count = pyword(readword(f))
        neg_count = pyword(count)
        csum = (csum + count) & 0xffff          # add neg word count
        print('       neg_count=%06o, csum=%06o' % (neg_count&0xffff, csum))
        csum_word = readword(f)
        csum = (csum + csum_word) & 0xffff      # add checksum word
        print('       csum_word=%06o, csum=%06o' % (csum_word, csum))
        while neg_count < 0:
            word = readword(f)
            csum = (csum + word) & 0xffff
            print('       word=%06o, csum=%06o' % (word, csum))
            mymem.add(ldaddr, word)
            (op, fld) = disasmdata.disasmdata(word)
            mymem.putOp(ldaddr, op)
            mymem.putFld(ldaddr, fld)
            ldaddr += 1
            neg_count += 1
        csum &= 0xffff
        if csum != 0:
            #wx.MessageBox('Checksum error', 'Error', wx.OK | wx.ICON_ERROR)
            print('Checksum error, csum=%06o, expected 0' % csum)
            wx.MessageBox('Checksum error, got %06o, expected 0' % csum, 'Warning', wx.OK | wx.ICON_WARNING)

    # check for real start address
    if ldaddr != 0177777:
        # actual start address
        ac = readword(f)
        return (mymem, ldaddr & 0x7ffff, ac)

    return (mymem, None, None)

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
    result = dobody(f, mymem)
    if result is None:
        return (mymem, None, None)

    return result

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

def readword(f, first_byte=None):
    """Return the next word from the input file.

    f           handle of the input file
    first_byte  value of first byte of word

    Convert 16bit values to python integers
    """

    if first_byte is None:
        first_byte = readbyte(f)

    return (first_byte << 8) + readbyte(f)

def skipzeros(f):
    while True:
        val = readbyte(f)
        if val > 0:
            return val


if __name__ == "__main__":
    result = ptpimport('40tp_simpleDisplay.ptp')
    if result is None:
        print('Error reading input file.')
        sys.exit(10)

    (themem, start, ac) = result
    print('str(dir(themem))=%s' % str(dir(themem)))
    if start is not None:
        print('start=%06o, ac=%06o' % (start, ac))
    else:
        print('start=None, ac=None')

    addrlist = themem.keys()
    addrlist.sort()
    for addr in addrlist:
        (word, cycle, type, lab, ref) = mymem[addr]
        print "%s %s: %05o" % (addr, type, word)
