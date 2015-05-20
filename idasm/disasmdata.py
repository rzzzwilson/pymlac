#!/usr/bin/env python

"""
This module disassembles one imlac machine word into a data instruction
string.
"""

def disasmdata(word):
    result = ("DATA", "%06o" % word)
    return result

if __name__ == "__main__":
    for word in xrange(0177777):
        (op, fld) = disasmdata(word)
        print "%07o: %s %s" % (word, op, fld)
