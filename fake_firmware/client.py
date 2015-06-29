# -*- coding: utf-8 -*-

from twisted.internet.protocol import ServerFactory, Protocol

from datetime import datetime
from PIL import Image
from zlib import crc32
import math

from construct import Container
from construct.core import FieldError

from constants import *
from structs import *
import messages
from helpers import array_to_string, string_to_array


class Client(Protocol):
    delegate = None
    buf = ""

    # Twisted Protocol methods
    
    def connectionMade(self):
        self.delegate.evt_has_connection()
    
    def dataReceived(self, data):
        self.buf += data
        
        self.last_activity_timestamp = datetime.now()
        
        length_needed = self.expected_length()
        while len(self.buf) >= length_needed:
            message_data = self.buf[:length_needed]
            self.buf = self.buf[length_needed:]
            
            self.process_data(message_data)
            
            length_needed = self.expected_length()

    def connectionLost(self, reason):
        pass

    # ---------- #

    def dump_data(self, data, direction):
        print direction, " ".join('%02x' % ord(c) for c in data)

    def send(self, container):
        data = struct_common.build(container)
        self.transport.write(data)
        self.dump_data(data, "(O) ")

    def expected_length(self):
        try:
            response = struct_base.parse(self.buf)
            return response['size']
        except FieldError:
            return MINI_HEADER_BYTES

    def process_data(self, data):
        self.dump_data(data, "(I) ")

        common_data = struct_common.parse(data)
        messages.process_message(common_data, self)

    # ---------- #

    current_printer_status = [0,0,0]
    current_tags = set()
    printer_buffer = []
    tag_auto_insertion = True
    tag_auto_removal = True

    # ---------- #

    def get_tag(self, serial):
        return self.delegate.req_tag(serial)

    def write_tag(self, serial, block_from, data):
        self.delegate.evt_tag_has_new_data(serial, block_from, data)

    def mark_tag_ro_blocks(self, serial, block_from, qty):
        self.delegate.evt_tag_has_new_RO_status(serial, block_from, qty)


    def tag_inserted(self, serial, silent_insertion):
        self.current_tags.add(serial)

        if not silent_insertion:
            messages.send_tags_list([serial], self, True)

        if self.tag_auto_insertion:
            self.simulate_printer_insertion()


    def tag_removed(self, serial):
        self.current_tags.discard(serial)

    # ---------- #

    def reset_printer_buffer(self):
        self.printer_buffer = []

    def add_data_to_printer_buffer(self, data):
        self.printer_buffer += data

    def do_print(self):
        img_data = array_to_string(self.printer_buffer)

        print "Print size:", PRINTER_IMAGE_WIDTH, len(img_data) / PRINTER_IMAGE_WIDTH

        image = Image.fromstring("L", (PRINTER_IMAGE_WIDTH, len(img_data)/PRINTER_IMAGE_WIDTH), img_data)
        image = image.transpose(Image.ROTATE_270)
        image = image.transpose(Image.FLIP_TOP_BOTTOM)
        image = image.transpose(Image.FLIP_LEFT_RIGHT)

        image.save("output/printer_output_%s.jpg" % datetime.now().strftime("%Y%m%d_%I%M%S_%f"), "JPEG")

        self.delegate.evt_printer_do_print(image)

    def printer_ejected(self):
        if self.tag_auto_removal:
            self.current_tags = set()
            self.delegate.evt_printer_eject()

    def simulate_printer_insertion(self):
        messages.send_printer_status(0, 0, 0, MSG_EV_PUB, EVT_PRINTER_PAPER_OUT_1, self)
        messages.send_printer_status(1, 0, 0, MSG_EV_PUB, EVT_PRINTER_PAPER_OUT_2, self)
        messages.send_printer_status(1, 0, 0, MSG_EV_PUB, EVT_PRINTER_PAPER_INSERTED, self)
        self.current_printer_status = [1, 0, 0]

    def simulate_printer_removal(self):
        messages.send_printer_status(1, 1, 0, MSG_EV_PUB, EVT_PRINTER_PAPER_OUT_1, self)
        messages.send_printer_status(0, 0, 0, MSG_EV_PUB, EVT_PRINTER_PAPER_OUT_2, self)
        messages.send_paper_remove(self)
        self.current_printer_status = [0, 0, 0]

class FakeFirmwareFactory(ServerFactory):
    protocol = Client
    noisy = True
    delegate = None
    last_instance = None

    def buildProtocol(self, addr):
        # We expect only one connection, so we only redirect delegate messages to the last instance.
        instance = ServerFactory.buildProtocol(self, addr)
        instance.delegate = self.delegate
        self.last_instance = instance
        return instance

