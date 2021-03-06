__all__ = ['PRINTER_IMAGE_WIDTH', 'PROTOCOL_VERSION_1', 'MINI_HEADER_BYTES', 'MSG_COMMAND', \
'MSG_EV_PUB', 'MSG_ERROR', 'DEV_AGENT', 'DEV_PWR', 'DEV_PRINTER', 'DEV_RFID', 'DEV_BUZZER', 'CMD_AGENT_INIT', \
'INIT_RESPONSE_OK', 'CMD_PWR_SET_LEDS', 'CMD_PRINTER_GET_STATUS', 'CMD_PRINTER_LOAD_BUFFER', \
'CMD_PRINTER_PRINT', 'CMD_PRINTER_CLEAR_BUFFER', 'CMD_PRINTER_PAPER_REMOVE', 'CMD_PRINTER_PAPER_START', \
'CMD_PRINTER_LOAD_COMP_BUFFER', 'EVT_PRINTER_PAPER_INSERTED', 'EVT_PRINTER_PAPER_OUT_1', \
'EVT_PRINTER_PAPER_OUT_2', 'CMD_RFID_GET_TAGS', 'CMD_RFID_READ_BLOCK', 'CMD_RFID_READ_BLOCKS', \
'CMD_RFID_WRITE_BLOCK', 'CMD_RFID_WRITE_BLOCKS', 'CMD_RFID_IS_READONLY', 'CMD_RFID_SET_RO_BLOCK', \
'CMD_RFID_SET_RO_BLOCKS', 'EVT_RFID_NEW_TAG', 'CMD_BUZZER_BUZZ', 'CMD_BUZZER_BUZZ' \
]

PRINTER_IMAGE_WIDTH = 832

PROTOCOL_VERSION_1 = 0x01
MINI_HEADER_BYTES = 0x04

# Message Types

MSG_COMMAND = 0x01
MSG_EV_PUB = 0x06
MSG_ERROR = 0xFF

# Devices

DEV_AGENT = 0x00
DEV_PWR = 0x01
DEV_PRINTER = 0x02
DEV_RFID = 0x03
DEV_BUZZER = 0x07

# Commands for DEV_AGENT

CMD_AGENT_INIT = 0x00
INIT_RESPONSE_OK = 0x00

# Commands for DEV_PWR

CMD_PWR_SET_LEDS = 0x0C

# Commands for DEV_PRINTER

CMD_PRINTER_GET_STATUS = 0x00
CMD_PRINTER_LOAD_BUFFER = 0x02
CMD_PRINTER_PRINT = 0x03
CMD_PRINTER_CLEAR_BUFFER = 0x04
CMD_PRINTER_PAPER_REMOVE = 0x05
CMD_PRINTER_PAPER_START = 0x06
CMD_PRINTER_LOAD_COMP_BUFFER = 0x09
EVT_PRINTER_PAPER_INSERTED = 0x80
EVT_PRINTER_PAPER_OUT_1 = 0x81
EVT_PRINTER_PAPER_OUT_2 = 0x82

# Commands for DEV_RFID

CMD_RFID_GET_TAGS = 0x00
CMD_RFID_READ_BLOCK = 0x02
CMD_RFID_READ_BLOCKS = 0x03
CMD_RFID_WRITE_BLOCK = 0x04
CMD_RFID_WRITE_BLOCKS = 0x05
CMD_RFID_IS_READONLY = 0x06
CMD_RFID_SET_RO_BLOCK = 0x07
CMD_RFID_SET_RO_BLOCKS = 0x08
EVT_RFID_NEW_TAG = 0x80

# Commands for DEV_BUZZER

CMD_BUZZER_BUZZ = 0x01
