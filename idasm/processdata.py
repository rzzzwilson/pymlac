#!/usr/bin/env python

"""
This module takes one word value and processes it as a DATA word.
"""


import disasmdata


def process(mem, addr, cycle):
    code = mem.getCode(addr)
    (op, fld) = disasmdata.disasmdata(code)
    mem.putOp(addr, op)
    mem.putFld(addr, fld)
    mem.putCycle(addr, cycle)
