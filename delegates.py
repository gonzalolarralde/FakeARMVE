# -*- coding: utf-8 -*-

import tags

# All the glue code goes here

ALERT_INSPECTION = True

class UIDelegate(object):
    fake_firmware_factory = None
    silent_insertion = False

    # Data Requests
    def req_tag_list(self):
        return tags.get_tags()

    def req_tag_parsed(self, serial):
        return tags.parse_tag(serial)

    def req_printer_buffer_data(self):
        pass

    def req_printer_last_image(self):
        pass

    # Triggering Events
    def evt_simulate_insertion(self):
        self.fake_firmware_factory.last_instance.simulate_printer_insertion()

    def evt_simulate_removal(self):
        self.fake_firmware_factory.last_instance.simulate_printer_removal()

    def evt_silent_insertion_changed(self, new_value):
        self.silent_insertion = new_value

    def evt_auto_insertion_changed(self, new_value):
        self.fake_firmware_factory.last_instance.tag_auto_insertion = new_value

    def evt_auto_removal_changed(self, new_value):
        self.fake_firmware_factory.last_instance.tag_auto_removal = new_value

    def evt_tag_inserted(self, serial):
        self.fake_firmware_factory.last_instance.tag_inserted(serial, self.silent_insertion)

    def evt_tag_removed(self, serial):
        self.fake_firmware_factory.last_instance.tag_removed(serial)

    def evt_reset_tags(self):
        tags.reset_tags()

class FakeFirmwareDelegate(object):
    main_ui_frame_instance = None
    first_connection = True

    # Data Requests
    def req_tag(self, serial):
        return tags.get_tag(serial)

    # Triggering Events
    def evt_tag_has_new_data(self, serial, block_from, data):
        tags.write_tag(serial, block_from, data)
        self.main_ui_frame_instance.reload_data()

    def evt_tag_has_new_RO_status(self, serial, block_from, qty):
        tags.set_tag_ro(serial, block_from, qty)
        self.main_ui_frame_instance.reload_data()

    def evt_tag_ejected(self, tags):
        pass

    def evt_printer_do_print(self, image):
        self.main_ui_frame_instance.show_image(image)

    def evt_printer_eject(self):
        self.main_ui_frame_instance.unselect_all()

    def evt_has_connection(self):
        if self.first_connection:
            self.main_ui_frame_instance.go_ahead()
            self.first_connection = False
