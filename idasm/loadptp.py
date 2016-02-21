#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Import an imlac binary file.

Usage:

    import loadptp
    result = loadptp.import('test.ptp', memory=None)
    if result is None:
        print('Unrecognized block loader')
        return
    (loader, memory) = result
"""

import struct


# size of memory configured
MemSize = 04000

# size of block loader
LoaderSize = 0100


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

    return ((first_byte << 8) + second_byte, index)

def skipzeros(ptp_data, index):
    """Skip leading zeros in tape data.

    ptp_data  the tape data
    index     current index into ptp_data for next byte to read

    Returns None if off the end of the tape data.  Otherwise returns the index
    of the first byte to read after the zeros.
    """

    while True:
        val = ptp_data[index]
        if val > 0:
            return index
        index += 1

    return None

def read_blockloader(ptp_data, index, memory):
    """Read block loader into high memory.

    ptp_data  array of PTP data
    index     index of next byte to read in 'ptp_data'
    memory    dict() object to store data in

    Returns None if off the end of the tape data, else the index of the next
    byte to read from 'ptp_data'.
    """

    address = MemSize - LoaderSize
    numwords = LoaderSize
    while numwords > 0:
        result = get_word(ptp_data, index)
        if result is None:
            return None
        (data, index) = result
        memory[address] = data
        address += 1
        numwords = numwords - 1

    return index

def c8lds_loader(ptp_data, memory):
    """Load blocks according to the "Loading the PDS-1" document.

    ptp_data  array of PTP data
    memory    dict() object to store data in

    Characterized as 'c8lds' meaning an 8bit data word [C]ount, then a [L]oad
    address, then [D]ata words followed by a check[S]um.

    This PTP data has data blocks with the following format:
        data count (8 bits)
        load address (16 bits)
        data word 1 (16 bits)
        ...
        data word 'count' (16 bits)
        checksum (16 bits)

    The example on the last page of the doc has a example tape containing:
        004 000770 001061 100011 023775 037765 165054

    The 'checksum' is not well defined in the documentation: the checksum is
    the sum of all the contents modulo 077777.  Yet the example tape has a
    checksum of 165054.  It is assumed the doc is in error and the checksum
    is the sum of all the data words, module 177777.

    As there is no autostart mechanism, returns (None, None) on successful load.
    Returns None if there was nothing to load.
    """

    index = 0

    # skip initial zero leader
    index = skipzeros(ptp_data, index)
    if index is None:
        # empty tape
        return None

    index = read_blockloader(ptp_data, index, memory)
    if index is None:
        # short block loader?
        return None

    # now read data blocks
    while True:
        # skip any leading zeros
        index = skipzeros(ptp_data, index)
        if index is None:
            break

        # get data word count
        result = get_byte(ptp_data, index)
        if result is None:
            # premature end of tape?
            return None
        (count, index) = result

        # get block load address
        result = get_word(ptp_data, index)
        if result is None:
            # premature end of tape?
            return None
        (address, index) = result

        # read data words, store in memory and calculate checksum
        checksum = 0
        for _ in range(count):
            result = get_word(ptp_data, index)
            if result is None:
                # premature end of tape?
                return None
            (data, index) = result

            memory[address] = data
            address += 1
            checksum += data

        # check block checksum
        checksum = checksum & 0177777
        result = get_word(ptp_data, index)
        if result is None:
            # premature end of tape?
            return None
        (ptp_checksum, index) = result
        if ptp_checksum != checksum:
            # bad checksum
            return None

    # no auto-start mechanism, so
    return (None, None)


def lc16sd_handler(ptp_data, memory):
    """Load blocks according to the ...

    ptp_data  array of PTP data
    memory    dict() object to store data in

    Characterized as 'lc16sd' meaning [L]oad address, then a 16bit data word
    [C]ount, then a 16bit check[S]um, followed by one or more [D]ata words.

    This PTP data has data blocks with the following format:
        one word of load address (16bits)
        a word of data word count (16bits, complemented)
        a checksum word (16bits)
        one or more data words (16bits)

    If the load address word is negative the load is finished.

    There is an autostart mechanism in this blockloader.  Returns
    (start_address, start_ac) on successful load.

    Returns None if there was nothing to load.
    """

    index = 0

    # skip initial zero leader
    index = skipzeros(ptp_data, index)
    if index is None:
        # empty tape
        return None

    index = read_blockloader(ptp_data, index, memory)
    if index is None:
        # short block loader?
        return None

    # now read data blocks
    while True:
        # skip leading zeros, if any
        index = skipzeros(ptp_data, index)
        if index is None:
            break

        # get this block load address
        result = get_word(ptp_data, index)
        if result is None:
            return None     # premature end of tape?
        (address, index) = result
        # if block load address is negative, we are finished
        if address & 0x8000:
            # address 0177777 means 'no autostart'
            if address != 0177777:
                # we have an autostart
                result = get_word(ptp_data, index)
                if result is None:
                    return None     # premature end of tape?
                (start_ac, index) = result
                return (address & 0x7ffff, ac)
            else:
                return (None, None)

        # read data block, calculating checksum
        csum = address                      # start checksum with base address
        result = get_word(ptp_data, index)
        if result is None:
            return None         # premature end of tape?
        (count, index) = result
        count = pyword(count)
        neg_count = pyword(count)
        csum = (csum + count) & 0xffff          # add neg word count
        result = get_word(ptp_data, index)
        if result is None:
            return None         # premature end of tape?
        (csum_word, index) = result
        csum = (csum + csum_word) & 0xffff      # add checksum word
        while neg_count < 0:
            result = get_word(ptp_data, index)
            if result is None:
                return None     # premature end of tape?
            (word, index) = result
            csum = (csum + word) & 0xffff
            memory[address] = word
            address += 1
            neg_count += 1
        csum &= 0xffff
        if csum != 0:
            return None     # bad block checlsum

    # if we return here there is no autostart
    return (None, None)

def load3_handler(ptp_data, memory):
    return None

# list of recognized loaders and handlers
Loaders = [
           ('c8lds', c8lds_loader),
           ('lc16sd', lc16sd_handler),
           ('loader 3', load3_handler),
          ]

def load(filename, memory=None):
    """Import a PTP file.

    filename  path of the PTP file to load
    memory    a memory dict, if specified

    Returns None if there was a problem, else returns (loader, memory)
    where 'loader' is a string identifying the loader used and 'memory'
    is a dict object containing the loaded memory: {addr: contents, ...}.
    """

    # if no 'memory' provided, create a new one
    if not memory:
        memory = dict()

    # get entirety of PTP file into memory
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

# DEBUG
#    count = 0
#    for i in range(len(data)):
#        if count == 0:
#            print "%04o:" % i,
#        print '%03o' % ord(data[i]),
#        count += 1
#        if count >= 16:
#            print
#            count = 0
#    print

    # convert to array of integers
    ptp_data = [ord(x) for x in data]
#    print(str(ptp_data))

    # try loaders in order
    for (name, loader) in Loaders:
        print('Trying loader: %s' % name)
        result = loader(ptp_data, memory)
        print('name: %s, result=%s' % (name, str(result)))
        if result is not None:
            # success!
            print('%s successful!' % name)
            return result

    # if we get here, no loader was successful
    return None

if __name__ == '__main__':
    print('test.ptp')
    load('test.ptp')
    print('testx.ptp')
    load('testx.ptp')
