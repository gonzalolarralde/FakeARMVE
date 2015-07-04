# -*- coding: utf-8 -*-

from helpers import *
import struct
from construct import Container, Field, Struct, Bytes, UBInt8, UBInt16, SBInt16, \
Adapter, Array, LFloat32, GreedyRange, Embed, OptionalGreedyRange, UBInt32

from zlib import crc32

struct_tag = Struct("tag", UBInt8("token"), UBInt8("tag_type"), UBInt16("size"), \
                    Array(4, UBInt8("crc32")), Array(lambda c: c.size, UBInt8("user_data")))

struct_tag_apertura = Struct("TAG_APERTURA", UBInt16("num"), UBInt8("hour"), UBInt8("min"), \
                             UBInt8("people"), UBInt8("names_len"), \
                             Array(lambda c: c.names_len, Bytes("names", 1)), \
                             Array(lambda c: c.people, Bytes("types", 1)), \
                             Array(lambda c: c.people, Bytes("ids", 4)))

TOKEN = '97'

TAG_TYPE_TO_NAME = {
    0: 'TAG_VACIO',
    1: 'TAG_VOTO',
    2: 'TAG_ADMIN',
    3: 'TAG_PRESIDENTE_MESA',
    4: 'TAG_RECUENTO',
    5: 'TAG_APERTURA',
    6: 'TAG_DEMO',
    7: 'TAG_VIRGEN',
    127: 'TAG_RECUENTO_P1',
    128: 'TAG_RECUENTO_P2'
}

# Initial Tag List

TAGS = {}


def form_tag_data(type, data="", number_of_blocks=28):
    crc = string_to_array(struct.pack("i", crc32(data)))
    fragmentable_data = struct_tag.build(Container(token=int(TOKEN,16), tag_type=type, size=len(data), crc32=crc, user_data=string_to_array(data)))
    fragmented_data = [string_to_array(fragmentable_data[i:i+4]) for i in xrange(0, len(fragmentable_data), 4)]
    
    blocks  = [x+([0]*4)[0:4-len(x)] for x in fragmented_data]
    blocks += [[0]*4]*(number_of_blocks-len(blocks))

    return blocks

def reset_tags():
    global TAGS
    TAGS = {
        b"12345670": { "desc": u"Presidente de Mesa", "blocks": form_tag_data(3), "ro_blocks": [] },
        b"12345671": { "desc": u"Apertura Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345672": { "desc": u"Apertura Precargado", "blocks": form_tag_data(5, struct_tag_apertura.build(Container(
                num=15,
                hour=9,
                min=1,
                people=2,
                names_len=len(pack_string("Sterling;Roger;Draper;Don")),
                names=pack_string("Sterling;Roger;Draper;Don"),
                types=["0","0"],
                ids=[pack_slow([20201201], 27),pack_slow([20201202], 27)]
            )) ), "ro_blocks": range(0,27) },

        b"12345673": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345674": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345675": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345676": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345677": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345678": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345679": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345680": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345681": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345682": { "desc": u"Vacío", "blocks": form_tag_data(0), "ro_blocks": [] },
        b"12345690": { "desc": u"Voto Precargado", "blocks": form_tag_data(1, array_to_string([48, 54, 69, 74, 46, 49, 46, 49, 67, 78, 74, 32, 32, 53, 68, 73, 80, 49, 50, 48, 71, 79, 66, 49, 54, 56, 73, 78, 84, 49, 56, 48, 83, 69, 78, 50, 51, 51])), "ro_blocks": range(0,27) },
        b"12345691": { "desc": u"Administrador", "blocks": form_tag_data(2), "ro_blocks": [] },
        b"12345692": { "desc": u"Recuento Precargado", "blocks": form_tag_data(4), "ro_blocks": [] },
        b"12345693": { "desc": u"Demo", "blocks": form_tag_data(6), "ro_blocks": [] },
    }

reset_tags()

# Data save / reading implementations

def get_tag(serial):
    return TAGS[serial]

def write_tag(serial, block_from, data):
    TAGS[serial]["blocks"][block_from:len(data)] = data

def set_tag_ro(serial, block_from, blocks):
    TAGS[serial]["ro_blocks"] += range(block_from, blocks)

def get_tags():
    return TAGS

def parse_tag(serial):
    try:
        tag = get_tag(serial)
        tag_data = struct_tag.parse(array_to_string(sum(tag["blocks"], [])))

        if tag_data.token == int(TOKEN,16):
            return {
                "desc": tag["desc"] if "desc" in tag else u"Sin Descripción",
                "type": TAG_TYPE_TO_NAME[tag_data.tag_type],
                "length": tag_data.size,
                "crc": tag_data.crc32,
                "user_data": tag_data.user_data,
                "is_ro": len(tag["ro_blocks"]) > 0
            }
        else:
            return { "desc": "Tag Invalido", "type": "BAD_TOKEN", "length": 0, "crc": "", "user_data": "", "is_ro": False }
    except Exception, e:
        print e
        return { "desc": "Error", "type": "ERROR", "length": -1, "crc": "", "user_data": "", "is_ro": False, "error": e }


