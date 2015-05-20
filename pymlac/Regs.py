#!/usr/bin/python 

"""
Class to emulate the Imlac Registers (main cpu and display cpu).
"""


class Regs(object):
    DS = 0100000		# data switches

    PC = 040			# main CPU program counter
    L = 0				# main CPU link register
    AC = 0				# main CPU accumulator
    Sync40Hz = 1		# main CPU 40Hz flag register

    DPC = 0				# display CPU program counter
    DRS = [0, 0, 0, 0, 0, 0, 0, 0]	# display CPU ???
    DRSindex = 0			# display CPU ???
    DIB = 0				# display CPU ???
    DX = 0				# display CPU draw X register
    DY = 0				# display CPU draw Y register

    def clearSync40Hz(self):
        """Clear the 40Hz flag register."""

        self.Sync40Hz = 0
