# -*- coding: utf-8 -*-

import platform
import struct

from construct import Container
from construct.core import FieldError
from datetime import datetime
from time import sleep
from zlib import crc32

from constants import *
from structs import *
from helpers import *

MESSAGE_HANDLERS = []
DEBUG = True

def prepare_container(device, command, data="", msg_type=MSG_COMMAND):
    return Container(
        version=PROTOCOL_VERSION_1,
        device=device,
        msg_type=msg_type,
        size=7 + len(data),
        command=command,
        data=data)

def debug_msg(*args):
    if DEBUG:
        print(args)

def message_handler(device, commands):
    def message_handler_call(f):
        MESSAGE_HANDLERS.append((device, commands, f))
        return f
    return message_handler_call

def handler_for(device, command):
    for handler in MESSAGE_HANDLERS:
        valid_commands = handler[1] if isinstance(handler[1], list) else [handler[1]]
        if handler[0] == device and command in valid_commands:
            return handler[2]
    return None

def process_message(common_data, client):
    if common_data.msg_type != MSG_ERROR:
        print "date", datetime.now()
        print "msg_type", common_data.msg_type
        print "device", common_data.device
        print "command", common_data.command
        print "data", string_to_array(common_data.data)

        possible_handler = handler_for(common_data.device, common_data.command)

        if possible_handler is not None:
            possible_handler(common_data, client)
        else:
            print "command name", "UNKNOWN"

        print "-------------"
    else:
        print "err", common_data.command
        print "data", string_to_array(common_data.data)
        print "-------------"

# --------------------- #

def send_initialize_ok(client):
    res = Container(
        response_code=INIT_RESPONSE_OK,
        protocol_size=1,
        protocols=[1],
        model=string_to_array("RogelitoEV  "),
        serial_number=string_to_array("12345678"),
        build=string_to_array("123"),
        watchdog=0,
        free_ram=65535,
        free_print_mem=65535,
        free_page_mem=65535,
        machine_type=1)
    cmd = prepare_container(DEV_AGENT, CMD_AGENT_INIT, struct_initialize_ok.build(res))
    client.send(cmd)

def send_tags_list(tags, client, as_event = False):
    res = Container(
        number = len(tags),
        serial_number = [string_to_array(x) for x in tags],
        reception_level = [[100] for x in tags])
    cmd = prepare_container(DEV_RFID, CMD_RFID_GET_TAGS if not as_event else EVT_RFID_NEW_TAG, \
        struct_tags_list.build(res), MSG_COMMAND if not as_event else MSG_EV_PUB)

    client.send(cmd)

def send_block_data(tag, block_from, block_qty, multi_block, client):
    blocks_to_send = [Container(bytes=x) for x in tag["blocks"][block_from:block_qty+1]] # OOPS, for some reason the service expects one additional block to be sent, to compute CRC
    
    if not multi_block:
        cmd = prepare_container(DEV_RFID, CMD_RFID_READ_BLOCK,  struct_rfid_block.build  (blocks_to_send[0]))
    else:
        cmd = prepare_container(DEV_RFID, CMD_RFID_READ_BLOCKS, struct_rfid_blocks.build (blocks_to_send))
    
    client.send(cmd)

def send_printer_status(paper_out_1, paper_out_2, lever_open, msg_type, command, client):
    cmd = prepare_container(DEV_PRINTER, command, \
        struct_printer_get_status.build(Container(paper_out_1=paper_out_1, paper_out_2=paper_out_2, lever_open=lever_open)), \
        msg_type)

    client.send(cmd)

def send_paper_remove(client):
    cmd = prepare_container(DEV_PRINTER, CMD_PRINTER_PAPER_REMOVE, "", MSG_EV_PUB)
    client.send(cmd)

# --------------------- #

@message_handler(DEV_AGENT, CMD_AGENT_INIT)
def _(common_data, client):
    print "command name", "AAAA CMD_AGENT_INIT"
    send_initialize_ok(client)

@message_handler(DEV_PRINTER, CMD_PRINTER_GET_STATUS)
def _(common_data, client):
    print "command name", "CMD_PRINTER_GET_STATUS"
    current_printer_status = client.current_printer_status
    send_printer_status(current_printer_status[0], current_printer_status[1], current_printer_status[2], \
        MSG_COMMAND, CMD_PRINTER_GET_STATUS, client)

@message_handler(DEV_RFID, CMD_RFID_GET_TAGS)
def _(common_data, client):
    print "command name", "CMD_RFID_GET_TAGS"
    send_tags_list(client.current_tags, client)

@message_handler(DEV_RFID, CMD_RFID_READ_BLOCK)
def _(common_data, client):
    print "command name", "CMD_RFID_READ_BLOCK"
    x = struct_read_block.parse(common_data.data)
    print "serial_number", x.serial_number
    print "block", x.block

    send_block_data(client.get_tag(array_to_string(x.serial_number)), x.block, 1, False, client)

@message_handler(DEV_RFID, CMD_RFID_READ_BLOCKS)
def _(common_data, client):
    print "command name", "CMD_RFID_READ_BLOCKS"
    x = struct_read_blocks.parse(common_data.data)
    print "serial_number", x.serial_number
    print "block", x.block
    print "number", x.number

    # ToDo: Fix - For some reason I'm reading a block less than the number sent by the service
    send_block_data(client.get_tag(array_to_string(x.serial_number)), x.block, x.number+1, True, client) 


@message_handler(DEV_PRINTER, CMD_PRINTER_PAPER_REMOVE)
def _(common_data, client):
    print "command name", "CMD_PRINTER_PAPER_REMOVE"
    client.current_printer_status = [0,0,0]
    send_printer_status(client.current_printer_status[0], client.current_printer_status[1], client.current_printer_status[2], \
        MSG_COMMAND, CMD_PRINTER_PAPER_REMOVE, client)
    client.printer_ejected()

@message_handler(DEV_RFID, CMD_RFID_WRITE_BLOCK)
def _(common_data, client):
    print "command name", "CMD_RFID_WRITE_BLOCK"
    x = struct_write_block.parse(common_data.data)
    print "serial_number", array_to_string(x.serial_number)
    print "block", x.block
    print "bytes", x.rfid_block.bytes

    client.write_tag(array_to_string(x.serial_number), x.block, [x.rfid_block.bytes])

    client.send(prepare_container(common_data.device, common_data.command))

@message_handler(DEV_RFID, CMD_RFID_WRITE_BLOCKS)
def _(common_data, client):
    print "command name", "CMD_RFID_WRITE_BLOCKS"
    x = struct_write_blocks.parse(common_data.data)
    print "serial_number", array_to_string(x.serial_number)
    print "block", x.block
    print "number", x.number
    print "bytes", [i.bytes for i in x.rfid_block]

    client.write_tag(array_to_string(x.serial_number), x.block, [i.bytes for i in x.rfid_block])

    client.send(prepare_container(common_data.device, common_data.command))

@message_handler(DEV_RFID, CMD_RFID_SET_RO_BLOCK)
def _(common_data, client):
    print "command name", "CMD_RFID_SET_RO_BLOCK"
    x = struct_read_block.parse(common_data.data)
    print "serial_number", array_to_string(x.serial_number)
    print "block", x.block

    client.mark_tag_ro_blocks(array_to_string(x.serial_number), x.block, 1)

@message_handler(DEV_RFID, CMD_RFID_SET_RO_BLOCKS)
def _(common_data, client):
    print "command name", "CMD_RFID_SET_RO_BLOCKS"
    x = struct_read_blocks.parse(common_data.data)
    print "serial_number", array_to_string(x.serial_number)
    print "block", x.block
    print "number", x.number

    client.mark_tag_ro_blocks(array_to_string(x.serial_number), x.block, x.number)

@message_handler(DEV_RFID, CMD_RFID_IS_READONLY)
def _(common_data, client):
    print "command name", "CMD_RFID_IS_READONLY"
    x = struct_read_blocks.parse(common_data.data)
    print "serial_number", array_to_string(x.serial_number)
    print "block", x.block
    print "number", x.number

    ro_blocks = client.get_tag(x.serial_number)["ro_blocks"]
    security_data = struct_security_status.build(Container(byte=[1 if x in ro_blocks else 0 for x in range(x.block, x.number)]))
    client.send(prepare_container(common_data.device, common_data.command, security_data))

@message_handler(DEV_PRINTER, CMD_PRINTER_CLEAR_BUFFER)
def _(common_data, client):
    client.reset_printer_buffer()

@message_handler(DEV_PRINTER, [CMD_PRINTER_LOAD_COMP_BUFFER, CMD_PRINTER_LOAD_BUFFER])
def _(common_data, client):
    x = struct_print_buffer.parse(common_data.data)
    if x.clear_buffer > 0:
        client.reset_printer_buffer()

    # print len(data), len(x.stream), size, x.size

    stream_data = x.stream
    if common_data.command == CMD_PRINTER_LOAD_COMP_BUFFER: # Expand the data if it compressed
        stream_data = expand_printer_data(stream_data)

    client.add_data_to_printer_buffer(stream_data)

    if x.do_print > 0:
        client.do_print()

