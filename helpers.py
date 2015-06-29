# -*- coding: utf-8 -*-

__all__ = ['pack_slow', 'unpack_slow', 'pack_string', 'string_to_array', 'array_to_string', 'expand_printer_data']

from bitarray import bitarray

STRING_PACKING_DICT = {chr(x+64):bitarray(bin(x)[2:].rjust(5,"0")) for x in range(1,27)}
STRING_PACKING_DICT.update( { " ": bitarray('11011'), "'": bitarray('11100'), u"Ñ": bitarray('11101'), " ": bitarray('11110'), ";": bitarray('11111') } )

def pack_slow(vals, bits=9):
    return sum([bitarray((bin(val)[2:]).rjust(bits,"0"))[0:bits] for val in vals], bitarray()).tobytes()

def unpack_slow(val, bits=9):
    ba = bitarray()
    ba.frombytes(val)
    return [int(ba[x:x+bits].to01(), 2) for x in range(0, len(ba) - (len(ba) % bits), bits)]

def pack_string(string):
    ba = bitarray()
    ba.encode(STRING_PACKING_DICT, string.upper())
    return ba.tobytes()

def string_to_array(string):
    return [ord(x) for x in list(string)]

def array_to_string(array):
    return "".join([chr(c) for c in array])

def expand_printer_data(data):
    # The byte format received is first bit for color (1=FF 0=00) and 7 bits for repeat count
    res = []
    for val in data:
        res += [0xFF if (val & 0x80) else 0x00] * (val & 0x7F)
    return res