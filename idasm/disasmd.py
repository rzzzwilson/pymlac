#!/usr/bin/env python

"""
This module disassembles one imlac machine word into a display processor
instruction string.

Note that this routine has state - if a DEIM instruction is found, the *next*
instruction is treated as part of the DEIM.
"""

mode = "NONE"


def disasmd(word):
    global mode
    result = None
    if mode == "DEIM":
        return deimword(word)
    else:
        opcode = word & 0070000
        if   opcode == 0000000: result = doGrpZero(word)
        elif opcode == 0010000: result = ("DLXA", "%05o" % (word & 07777))
        elif opcode == 0020000: result = ("DLYA", "%05o" % (word & 07777))
        elif opcode == 0030000:
            mode = "DEIM"
            result = ("DEIM", "%s"   % deimbyte(word & 0377))
        elif opcode == 0040000: result = ("DLVH", "%05o" % (word & 03777))
        elif opcode == 0050000: result = ("DJMS", "%05o" % (word & 07777))
        elif opcode == 0060000: result = ("DJMP", "%05o" % (word & 07777))
        else: result = ("DATA", "%06o" % word)
    return result

def doGrpZero(word):
    if   word == 0000000: return ("DHLT", "")
    elif word == 0004000: return ("DNOP", "")
    elif word == 0004004: return ("DSTS", "0")
    elif word == 0004005: return ("DSTS", "1")
    elif word == 0004006: return ("DSTS", "2")
    elif word == 0004007: return ("DSTS", "3")
    elif word == 0004010: return ("DSTB", "0")
    elif word == 0004011: return ("DSTB", "1")
    elif word == 0004020: return ("DDSP", "")
    elif word == 0005000: return ("DIXM", "")
    elif word == 0004400: return ("DIYM", "")
    elif word == 0004040: return ("DRJM", "")
    elif word == 0004200: return ("DDXM", "")
    elif word == 0004100: return ("DDYM", "")
    elif word == 0006000: return ("DHVC", "")
    elif word == 0004015: return ("DOPR", "15")
    elif word == 0004014: return ("DOPR", "14")
    else: return ("DATA", "%06o" % word)
    return None

def deimbyte(byte):
    global mode
    byte = byte & 0377
    if byte & 0200:
        beam = 'D'
        xsign = '+'
        ysign = '+'
        if byte & 0100: beam = 'B'
        if byte & 0040: xsign = '-'
        if byte & 0004: ysign = '-'
        return "%c%c%d%c%d" % \
                (beam, xsign, (byte & 0030) >> 3, ysign, (byte & 0003))
    else:
        esc = '_'
        ret = '_'
        xinc = '_'
        xzero = '_'
        yinc = '_'
        yzero = '_'
        if byte & 0100:
            mode = "NONE"
            esc = 'F'
        if byte & 0040:
            mode = "NONE"
            ret = 'R'
        if byte & 0020: xinc = '+'
        if byte & 0010: xzero = '0'
        if byte & 0002: yinc = '+'
        if byte & 0001: yzero = '0'
        return "%c%c%c%c%c%c" % (esc, ret, xinc, xzero, yinc, yzero)

def deimword(word):
    result = ("%s" % deimbyte(word >> 8), "%s" % deimbyte(word & 0377))
    return result


if __name__ == "__main__":
    for word in xrange(0177777 + 1):
        result = disasmd(word)
        print "%s %s" % result
