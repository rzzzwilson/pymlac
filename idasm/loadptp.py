#!/usr/bin/env python
# coding: utf-8

"""
Load a PTP file handling various formats.

Usage:

    import loadptp
    result = loadptp.load('test.ptp')
    if result:
        (format, memory, start, initial_ac) = result
        print('test.ptp is %s format' % format)
    else:
        print('UNKNOWN FORMAT')
"""

#from __future__ import (absolute_import, division, print_function, unicode_literals)
import struct


# size of the Imlace memory
MemSize = 04000

# size of block loader
LoaderSize = 0100

# True if debug code is active
Debug = True


def debug(msg):
    """Debug message, but only if global Debug is True."""

    if Debug:
        print(msg)

def pyword(word):
    """Convert a 16bit value to a real python integer.

    That is, convert 0xFFFF to -1.
    """

    byte = (word >> 8) & 0xff
    byte2 = word & 0xff
    bstr = chr(byte) + chr(byte2)
    return struct.unpack(">h", bstr)[0]

def get_byte(ptp_data, index):
    """Return the next byte from the PTP data.

    ptp_data  the tape data
    index     current index into ptp_data for next byte to read

    Returns None if off the end of the tape data else a tuple (byte, index)
    where 'byte' is the 8bit value and 'index' is the index of the next byte
    to read from the data.
    """

    try:
        result = ptp_data[index]
    except IndexError:
        return None

    return (result, index+1)

def get_word(ptp_data, index):
    """Return the next 16bit word from the PTP data.

    ptp_data  the tape data
    index     current index into ptp_data for next byte to read

    Returns None if off the end of the tape data else a tuple (word, index)
    where 'word' is the 16bit word value and 'index' is the index of the next
    byte to read from the data.

    Convert 16bit values to python integers
    """

    result = get_byte(ptp_data, index)
    if result is None:
        return None
    (first_byte, index) = result

    result = get_byte(ptp_data, index)
    if result is None:
        return None
    (second_byte, index) = result


    word = (first_byte << 8) + second_byte
    return (word, index)

def skipzeros(ptp_data, index):
    """Skip leading zeros in tape data.

    ptp_data  the tape data
    index     current index into ptp_data for next byte to read

    Returns None if off the end of the tape data.  Otherwise returns the index
    of the first byte to read after the zeros.
    """

    while True:
        try:
            val = ptp_data[index]
        except IndexError:
            # off end of tape
            return None
        if val > 0:
            return index
        index += 1

    return None

def read_blockloader(ptp_data, index, memory=None):
    """Skip over the block loader.

    ptp_data  array of PTP data
    index     index of next byte to read in 'ptp_data'
    memory    memory object to be populated with the loader code
              (if None, we aren't interested in the loader code)

    Returns None if off the end of the tape data, else the index of the next
    byte to read from 'ptp_data'.
    """

    if memory is None:
        memory = {}

    address = MemSize - LoaderSize
    numwords = LoaderSize
    while numwords > 0:
        result = get_word(ptp_data, index)
        if result is None:
            return None
        (data, index) = result
        memory[address] = data
        address += 1
        numwords -= 1

    return index

def c8lds_handler(ptp_data, memory, loader=False, body=False):
    """Sees if the PTP data follows the format in "Loading the PDS-1" document.

    ptp_data  array of PTP data
    memory    memory object to be populated with body code
    loader    True if we put loader code into memory
    body      True if we put body code into memory

    Returns None if PTP not recognized as 'c8lds'.
    Returns a tuple (None, None) if recognized.  This tuple is really
    (start, initialAC) but this format PTP file doesn't cater to those values.
    Note that the 'memory' may have been populated in either case.

    Characterized as 'c8lds' meaning an 8bit data word [C]ount, then a [L]oad
    address, then [D]ata words followed by a check[S]um.

    This PTP data has data blocks with the following format:
        data count (8 bits)
        load address (16 bits)
        data word 1 (16 bits)
        ...
        data word 'count' (16 bits)
        checksum (16 bits)
    Note that a data block may be preceded by a zero leader.

    The example on the last page of the doc has a example tape containing:
        004 000770 001061 100011 023775 037765 165054

    The 'checksum' is not well defined in the documentation which says: the
    checksum is the sum of all the contents modulo 077777.  Yet the example tape
    has a checksum of 0165054.  It is assumed the doc is in error and the
    checksum is the sum of all the data words, modulo 177777.

    A load address of 0177777 indicates the end of the load.
    Note that we DO need an 'end of load' block of three bytes at the end of
    the tape:
        377         # number of data words (any non-zero value will do)
        0177777     # a block load address of 0177777
    """

    index = 0

    if memory is None:
        memory = {}

    # skip initial zero leader
    index = skipzeros(ptp_data, index)
    if index is None:
        # empty tape
        debug('c8lds: No leader?')
        return None

    if loader:
        index = read_blockloader(ptp_data, index, memory=memory)
    else:
        unused_mem = {}
        index = read_blockloader(ptp_data, index, memory=unused_mem)

    if index is None:
        # short block loader?
        debug('c8lds: Short leader?')
        return None

    # now read data blocks
    if not body:
        memory = {}     # save body code into unused memory
    while True:
        index = skipzeros(ptp_data, index)
        if index is None:
            # empty tape
            debug('c8lds: EOT looking for block?')
            return None

        # get data word count
        result = get_byte(ptp_data, index)
        if result is None:
            # premature end of tape?
            debug('c8lds: EOT at start of block?')
            return None
        (count, index) = result
        debug('c8lds: word count=%03o' % count)

        # get block load address
        result = get_word(ptp_data, index)
        if result is None:
            # premature end of tape?
            debug('c8lds: EOT getting load address?')
            return None
        (address, index) = result
        debug('c8lds: load address=%06o' % address)
        if address == 0177777:
            # it's an End-Of-Tape block!
            return (None, None)

        # read data words, store in memory and calculate checksum
        checksum = 0
        for _ in range(count):
            result = get_word(ptp_data, index)
            if result is None:
                # premature end of tape?
                debug('c8lds: EOT getting data word?')
                return None
            (data, index) = result
            memory[address] = data
            debug('c8lds: data word=%06o' % data)

            address += 1
            checksum += data
            if checksum & 0177777 != checksum:
                # if overflow, increment before masking
                checksum += 1
            checksum = checksum & 0177777

        # check block checksum
        result = get_word(ptp_data, index)
        if result is None:
            # premature end of tape?
            debug('c8lds: EOT getting checksum?')
            return None
        (ptp_checksum, index) = result
        if ptp_checksum != checksum:
            # bad checksum
            debug('c8lds: Bad checksum? Read %06o, expected %06o.' % (ptp_checksum, checksum))
            return None

    # we shouldn't get here
    debug('c8lds: Badly formed PTP file')
    return None

def lc16sd_add_csum(csum, word):
    """Add 'csum' and 'word', return new checksum."""

    result = (csum + word) & 0xffff
    return result

def lc16sd_handler(ptp_data, memory, loader=False, body=False):
    """Decides if PTP data is in 'lc16sd' format.

    ptp_data  array of PTP data
    memory    memory object to be populated with body code
    loader    True if we put loader code into memory
    body      True if we put body code into memory

    Returns None if PTP not recognized as 'lc16sd'.
    Returns a tuple (start, initialAC) if recognized.
    Note that the 'memory' may have been populated in either case.

    Returns False if the PTP is not recognized as 'lc16sd'.
    Returns True if in 'lc16sd' format, else False.  Note that the 'memory' may
    have been populated in either case.

    Characterized as 'lc16sd' meaning [L]oad address, then a 16bit data word
    [C]ount, then a 16bit check[S]um, followed by one or more [D]ata words.

    This PTP data has data blocks with the following format:
        one word of load address (16bits)
        a word of data word count (16bits, complemented)
        a checksum word (16bits)
        one or more data words (16bits)

    The checksum is computed such that the sum of the load address, complemented
    word count, the checksum itself and all data words will be zero, modulo
    0177777.

    If the load address word is negative the load is finished.  The load address
    is the value put into the AC just before start.
    """

    index = 0

    # skip initial zero leader
    index = skipzeros(ptp_data, index)
    if index is None:
        # empty tape
        debug('lc16sd: No leader?')
        return None

    if loader:
        index = read_blockloader(ptp_data, index, memory=memory)
    else:
        unused_mem = {}
        index = read_blockloader(ptp_data, index, memory=unused_mem)

    if index is None:
        # short block loader?
        debug('lc16sd: Short blockloader?')
        return None

    # now read data blocks
    if not body:
        memory = {}
    while True:
        # get this block load address
        result = get_word(ptp_data, index)
        if result is None:
            debug('lc16sd: EOT getting load address?')
            return None     # premature end of tape?
        (address, index) = result
        # if block load address has high bit set, we are finished
        if address & 0x8000:
            # address 0177777 means 'no autostart'
            if address != 0177777:
                # we have an autostart
                result = get_word(ptp_data, index)
                if result is None:
                    debug('lc16sd: EOT getting AC value for autostart?')
                    return None     # premature end of tape?
                (initAC, index) = result
                return (address & 0x3fff, initAC)
            return (None, None)

        # read data block, calculating checksum
        csum = address                      # start checksum with base address
        debug('lc16sd: address=%06o' % address)
        result = get_word(ptp_data, index)
        if result is None:
            debug('lc16sd: EOT getting word count?')
            return None         # premature end of tape?
        (count, index) = result
        neg_count = pyword(count)
        debug('lc16sd: count=%06o, neg_count=%d' % (count, neg_count))
        csum = lc16sd_add_csum(csum, neg_count)

        result = get_word(ptp_data, index)
        if result is None:
            debug('lc16sd: EOT getting checksum?')
            return None         # premature end of tape?
        (csum_word, index) = result
        debug('lc16sd: csum_word=%06o' % csum_word)
        old_csum = csum
        csum = lc16sd_add_csum(csum, csum_word)

        # read body code, updating memory
        while neg_count < 0:
            result = get_word(ptp_data, index)
            if result is None:
                debug('lc16sd: EOT getting data word?')
                return None     # premature end of tape?
            (word, index) = result
            debug('lc16sd: data word=%06o' % word)
            old_csum = csum
            csum = lc16sd_add_csum(csum, word)
            memory[address] = word
            address += 1
            neg_count += 1
        if csum != 0:
            debug('lc16sd: Bad checksum, sum is %06o, expected 0?' % csum)
            return None     # bad block checksum

    # on a well-formed 'lc16sd' file we shouldn't get here
    debug('lc16sd: Badly formed file')
    return None

# list of recognized loaders and handlers
Loaders = [
           ('c8lds', c8lds_handler),
           ('lc16sd', lc16sd_handler),
          ]

def load(filename, loader=False, body=False):
    """Load a PTP file into a memory object after figuring out its format.

    filename  path of the PTP file to inspect
    loader    True if the blockloader code is to be loaded
    body      True if the body code is to be loaded

    Returns None if there was a problem, else returns a tuple
        (loader, memory, start, initial_ac)
    where the 'loader'      string identifies the loader,
              'memory'      is a memory object holding the loaded code,
              'start'       is the start addres, if any
              'initial_ac'  is the initial contents of AC
    """

    # get all of PTP file into memory
    data = None
    try:
        with open(filename, 'rb') as handle:
            data = handle.read()
    except IOError as e:
        print("Error opening '%s': %s" % (filename, e.strerror))
        return None

    if data is None:
        print("File '%s' is empty" % filename)
        return None

    # convert to array of integers
    ptp_data = [ord(x) for x in data]

    # try loaders in order
    for (name, loader) in Loaders:
        try:
            memory = {}
            result = loader(ptp_data, memory, loader=loader, body=body)
            debug('%s: result=%s' % (name, str(result)))
        except IndexError:
            result = None
        if result is not None:
            (start_addr, initial_ac) = result
            return (name, memory, start_addr, initial_ac)

    return None


if __name__ == '__main__':
    import sys

    def usage(msg=None):
        """Print usage and optional error message."""

        if msg:
            print('*'*60)
            print(msg)
            print('*'*60)
        print('Usage: loadptp <filename>')
        sys.exit(10)

    if len(sys.argv) < 2:
        usage()
    for filename in sys.argv[1:]:
        result = load(filename, loader=True, body=True)
        debug('top: result=%s' % str(result))
        if result is not None:
            (loader, memory, start, initial_ac) = result
            start_str = ''
            if start:
                start_str = ', start address is %06o' % start
            initial_ac_str = ''
            if initial_ac:
                initial_ac_str = ', initial AC is %06o' % initial_ac
            print('%14s: %s%s%s' % (loader, filename, start_str, initial_ac_str))
        else:
            print('UNRECOGNIZED: %s' % filename)
