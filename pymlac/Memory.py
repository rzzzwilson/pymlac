#!/usr/bin/python

"""
Emulate the Imlac Memory.
"""


import struct

from Globals import *
import Trace

import log
log = log.Log('test.log', log.Log.DEBUG)



class Memory(object):

    ROM_START = 0o40
    ROM_SIZE = 0o40
    ROM_END = ROM_START + ROM_SIZE - 1

    # this PTR bootstrap from "Loading The PDS-1" (loading.pdf)
    PTR_ROM_IMAGE = [          #         org     040
                     0o060077, # start   lac     base    ;40 get load address
                     0o020010, #         dac     010     ;41 put into auto-inc reg
                     0o104076, #         lwc     076     ;42 -0100+1 into AC
                     0o020020, #         dac     020     ;43 put into memory
                     0o001061, #         hon             ;44 start PTR
                     0o100011, # wait    cal             ;45 clear AC+LINK
                     0o002400, #         hsf             ;46 skip if PTR has data
                     0o010046, #         jmp     .-1     ;47 wait until is data
                     0o001051, #         hrb             ;50 read PTR -> AC
                     0o074075, #         sam     what    ;51 skip if AC == 2
                     0o010045, #         jmp     wait    ;52 wait until PTR return 0
                     0o002400, # loop    hsf             ;53 skip if PTR has data
                     0o010053, #         jmp     .-1     ;54 wait until is data
                     0o001051, #         hrb             ;55 read PTR -> AC
                     0o003003, #         ral     3       ;56 move byte into high AC
                     0o003003, #         ral     3       ;57
                     0o003002, #         ral     2       ;60
                     0o102400, #         hsn             ;61 wait until PTR moves
                     0o010061, #         jmp     .-1     ;62
                     0o002400, #         hsf             ;63 skip if PTR has data
                     0o010063, #         jmp     .-1     ;64 wait until is data
                     0o001051, #         hrb             ;65 read PTR -> AC
                     0o120010, #         dac     *010    ;66 store word, inc pointer
                     0o102400, #         hsn             ;67 wait until PTR moves
                     0o010067, #         jmp     .-1     ;70
                     0o100011, #         cal             ;71 clear AC & LINK
                     0o030020, #         isz     020     ;72 inc mem and skip zero
                     0o010053, #         jmp     loop    ;73 if not finished, jump
                     0o110076, #         jmp     *go     ;74 execute loader
                     0o000002, # what    data    2       ;75
                     0o003700, # go      data    03700   ;76
                     0o003677, # base    data    03677   ;77
                    ]

    TTY_ROM_IMAGE_TEST = [
          #00040   0001:         org     040
0o100001,  #00040   0002: loop    cla             ; clear AC
0o001031,  #00041   0003:         rrb             ; IOR tty input -> AC
0o010040,  #00042   0004:         jmp     loop    ; keep going
           #        0005:         end
                         ]

    # TTY ROM image from "Loading The PDS-1" (loading.pdf)
    TTY_ROM_IMAGE = [
          #        0001: ;------------------------
          #        0002: ; TTY bootstrap code from images/imlacdocs/loading.pdf
          #        0003: ;------------------------
          #        0004:                         ;
          #37700   0005: bladdr  equ     037700  ; address of top mem minus 0100
          #00100   0006: blsize  equ     0100    ; size of blockloader code
          #        0007:                         ;
          #00040   0008: 	ORG	040      ;
          #        0009:                         ;
0o060077, #00040   0010: 	LAC	staddr   ;
0o020010, #00041   0011: 	DAC	010      ; 010 points to loading word
0o104076, #00042   0012: 	LWC	blsize-2 ;
0o020020, #00043   0013: 	DAC	020      ; 020 is ISZ counter of loader size
          #        0014: ; skip all bytes until the expected byte
0o001032, #00044   0015: skpzer	RCF              ;
0o100011, #00045   0016: 	CAL              ;
0o002040, #00046   0017: 	RSF              ; wait for next byte
0o010046, #00047   0018: 	JMP	.-1      ;
0o001031, #00050   0019: 	RRB              ; get next TTY byte
0o074075, #00051   0020: 	SAM	fbyte    ; wait until it's the expected byte
0o010044, #00052   0021: 	JMP	skpzer   ;
0o002040, #00053   0022: nxtwrd	RSF              ; wait until TTY byte ready
0o010053, #00054   0023: 	JMP	.-1      ;
0o001033, #00055   0024: 	RRC              ; get high byte and clear flag
0o003003, #00056   0025: 	RAL	3        ; shift into AC high byte
0o003003, #00057   0026: 	RAL	3        ;
0o003002, #00060   0027: 	RAL	2        ;
0o002040, #00061   0028: 	RSF              ; wait until next TTY byte
0o010061, #00062   0029: 	JMP	.-1      ;
0o001033, #00063   0030: 	RRC              ; get low byte and clear flag
0o120010, #00064   0031: 	DAC	*010     ; store word
0o100011, #00065   0032: 	CAL              ; clear AC ready for next word
0o030020, #00066   0033: 	ISZ	020      ; finished?
0o010053, #00067   0034: 	JMP	nxtwrd   ; jump if not
0o110076, #00070   0035: 	JMP	*blstrt  ; else execute the blockloader
          #        0036:                         ;
0o000000, #00071   0037: 	DATA	000000   ; empty space?
0o000000, #00072   0038: 	DATA	000000   ;
0o000000, #00073   0039: 	DATA	000000   ;
0o000000, #00074   0040: 	DATA	000000   ;
          #        0041:                         ;
0o000002, #00075   0042: fbyte	DATA	000002   ; expected first byte of block loader
0o037700, #00076   0043: blstrt	data	bladdr   ; start of blockloader code
0o037677, #00077   0044: staddr	data	bladdr-1 ; ISZ counter for blockloader size
          #        0045:                         ;
          #        0046: 	END              ;
                    ]

    # class instance variables
    corefile = None
    memory = []
    using_rom = True
    boot_rom = None
    rom_protected = False


    def __init__(self, boot_rom=None, core=None):
        """   """

        self.corefile = core
        self.boot_rom = boot_rom
        self.memory = [0]*MEMORY_SIZE
        self.using_rom = boot_rom in [ROM_PTR, ROM_TTY]
        self.rom_protected = self.using_rom

        if self.corefile:
            try:
                self.loadcore(self.corefile)
            except IOError:
                self.clear_core()
        else:
            self.clear_core()

        self.set_ROM(self.boot_rom)

    def set_corefile(self, corefile):
        """Set name of the core save/restore file."""

        self.corefile = corefile

    def clear_core(self):
        """Clears memory to all zeros.

        If using ROM, that is unchanged.
        """

        for address in range(MEMORY_SIZE):
            if not self.rom_protected or not (self.ROM_START <= address <= self.ROM_END):
                self.memory[address] = 0

    def loadcore(self, filename=None):
        """Load core from a file.  Read 16 bit values as big-endian."""

        if not filename:
            filename = self.corefile

        self.memory = []
        try:
            with open(filename, 'rb') as fd:
                while True:
                    high = fd.read(1)
                    if high == '':
                        break
                    low = fd.read(1)
                    val = (ord(high) << 8) + ord(low)

                    self.memory.append(val)
        except struct.error:
            raise RuntimeError('Core file %s is corrupt!' % filename)

    def savecore(self, filename=None):
        """Save core in a file.  Write 16 bit values big-endian."""

        if not filename:
            filename = self.corefile

        with open(filename, 'wb') as fd:
            for val in self.memory:
                high = val >> 8
                low = val & 0xff

                fd.write(chr(high))
                fd.write(chr(low))

    def set_PTR_ROM(self):
        """Set addresses 040 to 077 as PTR ROM."""

        log('setting PTR bootstrap into ROM')
        i = self.ROM_START
        for ptr_value in self.PTR_ROM_IMAGE:
            self.memory[i] = ptr_value
            i += 1

    def set_TTY_ROM(self):
        """Set addresses 040 to 077 as TTY ROM."""

        log('setting TTY bootstrap into ROM')
        i = self.ROM_START
        for tty_value in self.TTY_ROM_IMAGE:
        #for tty_value in self.TTY_ROM_IMAGE_TEST:
            self.memory[i] = tty_value
            i += 1

    def set_ROM(self, romtype=None):
        """Set ROM to either PTR or TTY, or disable ROM."""

        save_flag = self.rom_protected
        self.rom_protected = False
        if romtype == 'ptr':
            self.set_PTR_ROM()
            self.rom_protected = True
        elif romtype == 'tty':
            self.set_TTY_ROM()
            self.rom_protected = True
        else:
            self.rom_protected = save_flag

    def set_ROM_writable(self, writable):
        """Set ROM write protection state."""

        self.rom_protected = writable

    def fetch(self, address, indirect):
        """Get a value from a memory address.

        The read can be indirect, and may be through an
        auto-increment address.
        """

        # the Imlac can get into infinite defer loops, and so can we!
        while indirect:
            address = MASK_MEM(address)

            # if indirect on auto-inc register, add one to it before use
            if ISAUTOINC(address):
                self.memory[address] += 1
            address = self.memory[MASK_MEM(address)]
            indirect = bool(address & 0o100000)

        return self.memory[MASK_MEM(address)]

    def eff_address(self, address, indirect):
        """Get an effective memory address.

        The address can be indirect, and may be through an
        auto-increment address.
        """

        # the Imlac can get into infinite defer loops, and so can we!
        while indirect:
            if ISAUTOINC(address):
                # indirect on auto-inc register, add one to it before use
                self.memory[address] = MASK_MEM(self.memory[address] + 1)
            try:
                address = self.memory[address]
            except IndexError:
                # assume we are addressing out of memory limits
                msg = 'Bad memory address: %06o' % address
                raise IndexError(msg)
            indirect = bool(address & 0o100000)

        return address

    def str_trace(self, msg=None):
        """Get a traceback string."""

        import traceback

        result = []

        if msg:
            result.append(msg+'\n')

        result.extend(traceback.format_stack())

        return ''.join(result)

    def put(self, value, address, indirect):
        """Put a value into a memory address.

        The store can be indirect, and may be through an
        auto-increment address.
        """

        # limit memory to available range
        address = address & PCMASK

        if indirect:
            address = self.memory[address] & ADDRMASK

        # limit memory to available range
        address = address & PCMASK

        if self.rom_protected and self.ROM_START <= address <= self.ROM_END:
            print('Attempt to write to ROM address %07o' % address)
            Trace.comment('Attempt to write to ROM address %07o' % address)
            return

        try:
            self.memory[address] = MASK_16(value)
        except IndexError:
            raise RuntimeError('Bad address: %06o (max mem=%06o, ADDRMASK=%06o)'
                               % (address, len(self.memory), ADDRMASK))

    def dump(self, low, high):
        """Dump memory in range [low, high] inclusive to a file."""

        with open('x.dump', 'wb') as fd:
            for i in range(high - low + 1):
                val = self.fetch(low + i, False)
                high = val >> 8
                low = val & 0xff
                data = struct.pack('B', high)
                fd.write(data)
                data = struct.pack('B', low)
                fd.write(data)

