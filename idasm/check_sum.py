#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Test code to determine the checksum algorithm used in Imlac PTP blocks.
"""

MASK = 0177777

# actual block from 40tp_simpleDisplay.ptp
block = [065,       # word count
         0000100,   # load address
         0001012, 0102010, 0010101, 0002200, 0010103, 0001071, 0100041, 0044164,    # data words
         0020111, 0000000, 0004116, 0001003, 0003100, 0010101, 0015000, 0025000,    # data words
         0004005, 0006000, 0050132, 0050141, 0050151, 0050151, 0050156, 0015000,    # data words
         0025000, 0000000, 0030303, 0141702, 0114230, 0143707, 0143203, 0100770,    # data words
         0174171, 0030303, 0141702, 0154330, 0127655, 0174350, 0103605, 0154330,    # data words
         0074571, 0030303, 0141702, 0000600, 0154330, 0074571, 0030202, 0141723,    # data words
         0150327, 0143766, 0170362, 0074571, 0100000,                               # data words
         0105226]   # checksum word

def checksum1(block):
    """Checksum is sum of data words, mask at end."""

    checksum = 0
    for word in block[2:-1]:
        checksum += word
    return checksum & MASK

def checksum2(block):
    """Checksum is sum of data words, mask at each sum and end."""

    checksum = 0
    for word in block[2:-1]:
        checksum = (checksum + word) & MASK
    return checksum & MASK

def checksum3(block):
    """Checksum is sum of load address and data words, mask at end."""

    checksum = block[1]
    for word in block[2:-1]:
        checksum += word
    return checksum & MASK

def checksum4(block):
    """Checksum is sum of load address and data words, mask at each sum and end."""

    checksum = block[1]
    for word in block[2:-1]:
        checksum = (checksum + word) & MASK
    return checksum & MASK

def checksum5(block):
    """Checksum is sum of word count, load address and data words,
    mask at end."""

    checksum = block[0]
    checksum += block[1]
    for word in block[2:-1]:
        checksum += word
    return checksum & MASK

def checksum6(block):
    """Checksum is sum of word count, load address and data words,
    mask at at each sum and end."""

    checksum = block[0]
    checksum = (checksum + block[1]) & MASK
    for word in block[2:-1]:
        checksum = (checksum + word) & MASK
    return checksum & MASK

def checksum7(block):
    """Checksum is sum of data words, mask at end.  Sum is +1 on overflow"""

    checksum = 0
    for word in block[2:-1]:
        checksum += word
        if checksum & MASK:
            checksum += 1
    return checksum & MASK

def checksum8(block):
    """Checksum is sum of load + data words, mask at end.  Sum is +1 on overflow"""

    checksum = block[1]
    for word in block[2:-1]:
        checksum += word
        if checksum & MASK:
            checksum += 1
    return checksum & MASK

def checksum9(block):
    """Checksum is sum of count+load+data words, mask at end.  Sum is +1 on overflow"""

    checksum = block[0]
    checksum += block[1]
    if checksum & MASK:
        checksum += 1
    for word in block[2:-1]:
        checksum += word
        if checksum & MASK:
            checksum += 1
    return checksum & MASK

csum1 = checksum1(block)
csum2 = checksum2(block)
csum3 = checksum3(block)
csum4 = checksum4(block)
csum5 = checksum5(block)
csum6 = checksum6(block)
csum7 = checksum7(block)
csum8 = checksum8(block)
csum9 = checksum9(block)

print('csum1=%06o' % csum1)
print('csum2=%06o' % csum2)
print('csum3=%06o' % csum3)
print('csum4=%06o' % csum4)
print('csum5=%06o' % csum5)
print('csum6=%06o' % csum6)
print('csum7=%06o' % csum7)
print('csum8=%06o' % csum8)
print('csum9=%06o' % csum9)

print('checksum should be 105226')
