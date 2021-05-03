import os
import re
import csv
import serial
from datetime import datetime


def handle_DPT1(value):
    VALUES = {0x81: 'on', 0x80: 'off'}

    return VALUES.get(value)


def handle_DPT3(value):
    dim_val = value & 0x7

    if (value & 0x8) == 8:
        return f'increase { dim_val }'

    return f'decrease { dim_val }'


class KnxSerial:
    DEVICE = '/dev/ttyAMA0'
    BAUDRATE = 19200
    CHARACTER_SIZE = serial.EIGHTBITS
    PARITY = serial.PARITY_EVEN


class Bytes:
    STARTBYTE = 0
    DEST_HIGH_BYTE = 11
    DEST_LOW_BYTE = 12
    PAYLOAD = {'Byte0': 15}


class BytesValues:
    STARTBYTE = b'\x68'
    PAYLOAD = {
        'DPT1': {0x81: 'on', 0x80: 'off'}
    }
    STOPBYTE = b'\x16'


class DPTHandlers:
    PAYLOAD = {
        'DPT1': handle_DPT1,
        'DPT3': handle_DPT3,
    }


def check_startbyte(frame):
    first_byte_not_startbyte = frame and frame[Bytes.STARTBYTE] != BytesValues.STARTBYTE

    if first_byte_not_startbyte:
        frame.pop(Bytes.STARTBYTE)

    return frame


def get_groupaddress(frame):
    raw_address = f"{ frame[Bytes.DEST_HIGH_BYTE] } { frame[Bytes.DEST_LOW_BYTE] }"
    subaddress = frame[Bytes.DEST_LOW_BYTE]
    high_byte = frame[Bytes.DEST_HIGH_BYTE]
    midaddress_mask = 0x07
    midaddress = high_byte & midaddress_mask
    mainaddress = high_byte >> 3

    groupaddress = f'{ mainaddress }/{ midaddress }/{ subaddress }'

    return {'raw': raw_address, 'formatted': groupaddress}


def get_value(frame, datapoint_type):
    raw_value = frame[Bytes.PAYLOAD.get('Byte0')]
    DPTs = {
        'DPT1': '^DPS?T-1-',
        'DPT3': '^DPS?T-3-',
    }
    value = ''
    for dpt, pattern in DPTs.items():
        if re.match(pattern, datapoint_type):
            value = DPTHandlers.PAYLOAD.get(dpt)(raw_value)

    return {'raw': raw_value, 'formatted': value}


def writer(filename, groupaddress_info):
    with open(filename, "w", newline="") as csv_file:
        stati = csv.DictWriter(csv_file, fieldnames=groupaddress_info.keys())
        stati.writeheader()
        stati.writerow(groupaddress_info)


def updater(filename, groupaddress_info):
    with open(filename, newline="") as file:
        readData = [row for row in csv.DictReader(file)]
        found = False
        new_status = {}

        for index, raw in enumerate(readData):
            if groupaddress_info.get('groupaddress') in readData[index]['groupaddress']:
                readData[index]['status'] = groupaddress_info.get('status')
                found = True
                break

        if not found:
            new_status = groupaddress_info

    with open(filename, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=groupaddress_info.keys())
        writer.writeheader()
        writer.writerows(readData)

        if new_status:
            writer.writerow(new_status)


def save_status(groupaddress_info):
    FILEPATH = '/usr/local/gateway/'
    FILENAME = 'KNX_stati.csv'
    FILE = f"{ FILEPATH }{ FILENAME }"

    file_exists = os.path.isfile(FILE)

    if file_exists:
        updater(FILE, groupaddress_info)

    else:
        writer(FILE, groupaddress_info)


def get_groupaddress_info(groupaddress):
    FILE = '/usr/local/gateway/ga.csv'

    with open(FILE) as groupaddresses_info:
        data = [info for info in csv.DictReader(
            groupaddresses_info) if groupaddress in info.get('Address')]

    info = data[0]

    return {
        'groupaddress': info.get('Address'),
        'groupaddress name': info.get('Group name'),
        'datapoint type': info.get('DatapointType')
    }
