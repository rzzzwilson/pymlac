#!/usr/bin/env python

"""
This module implements the 'mem' object and access routines.

A 'mem' object is a dictionary with the form:

{ address: (code, op, fld, labcount, ref, type, cycle),
  address: (code, op, fld, labcount, ref, type, cycle),
   ...
}

where address    is the address of the data (integer)
      code       is the code value at the address (integer)
      op         is the opcode (string)
      fld        is the instruction field (string)
      labcount   is the number of references to this address (integer)
      ref        is a flag to show if this word references another (boolean)
      type       is type of processed instruction 'm' for main
                                                  'd' for display
                                                  None for none
      cycle      is the cycle number when this word was processed
"""


class Mem(object):

    def __init__(self):
        self.memory = {}
        self.undo = None

    def add(self, address, code):
        self.putMem(address, (code, "", "", 0, False, None, 0))
    
    def len(self):
        return len(self.memory)
    
    def getMem(self, address):
        addrstr = "%05o" % address
        result = self.memory.get(addrstr, None)
        if not result:
            result = (0, "", "", 0, False, None, 0)
            self.putMem(address, result)
        return result
    
    def getCode(self, address):
        (code, _, _, _, _, _, _) = self.getMem(address)
        return code
    
    def getOp(self, address):
        (_, op, _, _, _, _, _) = self.getMem(address)
        return op
    
    def getFld(self, address):
        (_, _, fld, _, _, _, _) = self.getMem(address)
        return fld
    
    def getLabcount(self, address):
        (_, _, _, labcount, _, _, _) = self.getMem(address)
        return labcount
    
    def getRef(self, address):
        (_, _, _, _, ref, _, _) = self.getMem(address)
        return ref
    
    def getType(self, address):
        (_, _, _, _, _, type, _) = self.getMem(address)
        return type
    
    def getCycle(self, address):
        (_, _, _, _, _, _, cycle) = self.getMem(address)
        return cycle
    
    def putMem(self, address, entry):
        addrstr = "%05o" % address
        self.memory[addrstr] = entry
    
    def putCode(self, address, code):
        (_, op, fld, labcount, ref, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putOp(self, address, op):
        (code, _, fld, labcount, ref, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putFld(self, address, fld):
        (code, op, _, labcount, ref, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putLabcount(self, address, labcount):
        (code, op, fld, _, ref, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putRef(self, address, ref):
        (code, op, fld, labcount, _, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putType(self, address, type):
        (code, op, fld, labcount, ref, _, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def putCycle(self, address, cycle):
        (code, op, fld, labcount, ref, type, _) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def decLab(self, address):
        (code, op, fld, labcount, ref, type, cycle) = self.getMem(address)
        labcount -= 1
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def incLab(self, address):
        (code, op, fld, labcount, ref, type, cycle) = self.getMem(address)
        labcount += 1
        self.putMem(address, (code, op, fld, labcount, ref, type, cycle))
    
    def clearRef(self, address):
        (code, op, fld, labcount, _, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, False, type, cycle))
    
    def setRef(self, address):
        (code, op, fld, labcount, _, type, cycle) = self.getMem(address)
        self.putMem(address, (code, op, fld, labcount, True, type, cycle))
    
    def keys(self):
        return self.memory.keys()

    def clearUndo(self):
        self.undo = None
    
    def setUndo(self):
        self.undo = self.memory.copy()
    
    def undoX(self):
        tmp = self.memory
        self.memory = self.undo
        self.undo = tmp
    
