import struct
from helpers import *

from construct import Field, Struct, UBInt8, UBInt16, SBInt16, Adapter, Array, LFloat32, GreedyRange, Embed, OptionalGreedyRange, UBInt32


class SmallNumber(Adapter):
    def _encode(self, obj, context):
        return struct.Struct(">L").pack(obj)[1:]

    def _decode(self, obj, context):
        return struct.unpack(">L", b"\x00" + obj)[0]


struct_base = Struct("base", UBInt8("version"), SmallNumber(Field("size", 3)))

struct_common = Struct("common", Embed(struct_base), UBInt8("msg_type"), \
                       UBInt8("device"), UBInt8("command"), Field("data", lambda c: c.size-7))

struct_initialize_ok = Struct("init_ok", UBInt8("response_code"), UBInt8("protocol_size"), \
                              Array(lambda c: c.protocol_size, UBInt8("protocols")), Array(12, UBInt8("model")), \
                              Array(8, UBInt8("serial_number")), Array(3, UBInt8("build")), UBInt8("watchdog"), \
                              UBInt32("free_ram"), UBInt32("free_print_mem"), UBInt32("free_page_mem"), UBInt8("machine_type"))

struct_led = Struct("led", UBInt8("leds"), UBInt8("color"), UBInt16("period"), UBInt16("timeout"))

struct_printer_get_status = Struct("printer_get_status", UBInt8("paper_out_1"), UBInt8("paper_out_2"), \
                                   UBInt8("lever_open"))

struct_print_buffer = Struct("print_buffer", UBInt16("size"), Array(lambda c: c.size, UBInt8("stream")), \
                             UBInt8("do_print"), UBInt8("clear_buffer"))

struct_tags_list = Struct("tags_list", UBInt8("number"), Array(lambda c: c.number, Array(8, UBInt8("serial_number"))), \
                          Array(lambda ctx: ctx.number, Array(1, UBInt8("reception_level"))))

struct_rfid_block = Struct("rfid_block", Array(4, UBInt8("bytes")))
struct_rfid_blocks = GreedyRange(struct_rfid_block)

struct_read_block = Struct("read_block", Array(8, UBInt8("serial_number")), UBInt8("block"))
struct_read_blocks = Struct("read_blocks", Embed(struct_read_block), UBInt8("number"))

struct_write_block = Struct("write_block", Embed(struct_read_block), Embed(struct_rfid_block))
struct_write_blocks = Struct("write_blocks", Embed(struct_read_blocks), GreedyRange(struct_rfid_block))

struct_byte = Struct("byte", UBInt8("byte"))
struct_security_status = GreedyRange(struct_byte)
