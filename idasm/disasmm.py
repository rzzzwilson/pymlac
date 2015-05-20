#!/usr/bin/env python

"""
This module disassembles one imlac machine word into a main processor
instruction string.  If the word isn't a legal instruction, return DATA.
"""


def disasmm(word):
    result = ("", "")
    opcode = word & 0174000
    if   opcode == 0000000: result = doGrpZero(word)
    elif opcode == 0004000: result = ("LAW", "%05o" % (word & 03777))
    elif opcode == 0104000: result = ("LWC", "%05o" % (word & 03777))
    elif opcode == 0010000: result = ("JMP", "%05o" % (word & 03777))
    elif opcode == 0110000: result = ("JMP", "*%05o" % (word & 03777))
    elif opcode == 0020000: result = ("DAC", "%05o" % (word & 03777))
    elif opcode == 0120000: result = ("DAC", "*%05o" % (word & 03777))
    elif opcode == 0024000: result = ("XAM", "%05o" % (word & 03777))
    elif opcode == 0124000: result = ("XAM", "*%05o" % (word & 03777))
    elif opcode == 0030000: result = ("ISZ", "%05o" % (word & 03777))
    elif opcode == 0130000: result = ("ISZ", "*%05o" % (word & 03777))
    elif opcode == 0034000: result = ("JMS", "%05o" % (word & 03777))
    elif opcode == 0134000: result = ("JMS", "*%05o" % (word & 03777))
    elif opcode == 0044000: result = ("AND", "%05o" % (word & 03777))
    elif opcode == 0144000: result = ("AND", "*%05o" % (word & 03777))
    elif opcode == 0050000: result = ("IOR", "%05o" % (word & 03777))
    elif opcode == 0150000: result = ("IOR", "*%05o" % (word & 03777))
    elif opcode == 0054000: result = ("XOR", "%05o" % (word & 03777))
    elif opcode == 0154000: result = ("XOR", "*%05o" % (word & 03777))
    elif opcode == 0060000: result = ("LAC", "%05o" % (word & 03777))
    elif opcode == 0160000: result = ("LAC", "*%05o" % (word & 03777))
    elif opcode == 0064000: result = ("ADD", "%05o" % (word & 03777))
    elif opcode == 0164000: result = ("ADD", "*%05o" % (word & 03777))
    elif opcode == 0070000: result = ("SUB", "%05o" % (word & 03777))
    elif opcode == 0170000: result = ("SUB", "*%05o" % (word & 03777))
    elif opcode == 0074000: result = ("SAM", "%05o" % (word & 03777))
    elif opcode == 0174000: result = ("SAM", "*%05o" % (word & 03777))
    elif opcode == 0100000: result = doMicroCode(word)
    else: result = ("DATA", "%07o" % word)

    return result

def doGrpZero(word):
    opcode = word & 0177000
    if opcode == 0000000:
        if word > 0:
            return ("HLT", "%d" % word)
        return ("HLT", "")
    elif opcode == 0003000: return doShRot(word)
    elif opcode == 0002000: return doSkipFlag(word)
    elif opcode == 0001000: return doIOT(word)
    else: print "DEFAULT"; return ("DATA", "%06o" % word)
    

def doShRot(word):
    opcode = word & 0177770
    if   opcode == 0003040: return ("SAL", "%d" % (word & 07))
    elif opcode == 0003060: return ("SAR", "%d" % (word & 07))
    elif opcode == 0003100: return ("DON", "")
    elif opcode == 0003000: return ("RAL", "%d" % (word & 07))
    elif opcode == 0003020: return ("RAR", "%d" % (word & 07))
    else: return ("DATA", "%06o" % word)
    return None

def doSkipFlag(word):
    if   word == 002001: return ("ASZ", "")
    elif word == 002002: return ("ASP", "")
    elif word == 002004: return ("LSZ", "")
    elif word == 002010: return ("DSF", "")
    elif word == 002020: return ("KSF", "")
    elif word == 002040: return ("RSF", "")
    elif word == 002100: return ("TSF", "")
    elif word == 002200: return ("SSF", "")
    elif word == 002400: return ("HSF", "")
    else: return ("DATA", "%06o" % word)
    return None

def doIOT(word):
    if   word == 001003: return ("DLA", "")
    elif word == 001011: return ("CTB", "")
    elif word == 001012: return ("DOF", "")
    elif word == 001021: return ("KRB", "")
    elif word == 001022: return ("KCF", "")
    elif word == 001023: return ("KRC", "")
    elif word == 001031: return ("RRB", "")
    elif word == 001032: return ("RCF", "")
    elif word == 001033: return ("RRC", "")
    elif word == 001041: return ("TPR", "")
    elif word == 001042: return ("TCF", "")
    elif word == 001043: return ("TPC", "")
    elif word == 001051: return ("HRB", "")
    elif word == 001052: return ("HOF", "")
    elif word == 001061: return ("HON", "")
    elif word == 001062: return ("STB", "")
    elif word == 001071: return ("SCF", "")
    elif word == 001072: return ("IOS", "")
    elif word == 001274: return ("PSF", "")
    elif word == 001271: return ("PPC", "")
    elif word == 001101: return ("IOT", "0101")
    elif word == 001141: return ("IOT", "0141")
    elif word == 001161: return ("IOT", "0161")
    elif word == 001162: return ("IOT", "0162")
    elif word == 001131: return ("IOT", "0131")
    elif word == 001132: return ("IOT", "0132")
    elif word == 001134: return ("IOT", "0134")
    else: return ("DATA", "%06o" % word)
    return None

def doMicroCode(word):
    if   word == 0100000: return ("NOP", "")
    elif word == 0100001: return ("CLA", "")
    elif word == 0100002: return ("CMA", "")
    elif word == 0100003: return ("STA", "")
    elif word == 0100004: return ("IAC", "")
    elif word == 0100005: return ("COA", "")
    elif word == 0100006: return ("CIA", "")
    elif word == 0100010: return ("CLL", "")
    elif word == 0100020: return ("CML", "")
    elif word == 0100011: return ("CAL", "")
    elif word == 0100030: return ("STL", "")
    elif word == 0100040: return ("ODA", "")
    elif word == 0100041: return ("LDA", "")
    elif word == 0102001: return ("ASN", "")
    elif word == 0102002: return ("ASM", "")
    elif word == 0102004: return ("LSN", "")
    elif word == 0102010: return ("DSN", "")
    elif word == 0102020: return ("KSN", "")
    elif word == 0102040: return ("RSN", "")
    elif word == 0102100: return ("TSN", "")
    elif word == 0102200: return ("SSN", "")
    elif word == 0102400: return ("HSN", "")
    else: return ("DATA", "%06o" % word)
    return None


if __name__ == "__main__":
    for word in xrange(0177777 + 1):
        (op, fld) = disasmm(word)
        print "%07o: %s %s" % (word, op, fld)
