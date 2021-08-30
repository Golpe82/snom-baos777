'''Module for reading telegrams from KNX bus'''
import os
import re
import csv
import requests
import logging

import datapoint_types


ETS_FILE = '/usr/local/gateway/iot/knx/media/ga.csv'
DEST_HIGH_BYTE = 11
DEST_LOW_BYTE = 12
PAYLOAD = {
    'Byte0': 15,
    'Byte1': 16,
}
POST_MONITOR_URL = "http://localhost:8000/knx/groupaddress_monitor"
POST_STATUS_URL = "http://localhost:8000/knx/status"

logging.basicConfig(level=logging.DEBUG)


def get_groupaddress(frame):
    raw_address = f"{ frame[DEST_HIGH_BYTE] } { frame[DEST_LOW_BYTE] }"
    subaddress = frame[DEST_LOW_BYTE]
    high_byte = frame[DEST_HIGH_BYTE]
    midaddress_mask = 0x07
    midaddress = high_byte & midaddress_mask
    mainaddress = high_byte >> 0x03

    groupaddress = f'{ mainaddress }/{ midaddress }/{ subaddress }'

    return {'raw': raw_address, 'formatted': groupaddress}


def get_value(frame, datapoint_type):
    raw_value = frame[PAYLOAD.get('Byte0')]
    value = ''

    for dpt, pattern in datapoint_types.PATTERNS.items():
        if re.match(pattern, datapoint_type):
            handler = datapoint_types.DptHandlers(raw_value)
            value = handler.get_formatted_value(dpt)

    return {'raw': raw_value, 'formatted': value}


def get_groupaddress_info(groupaddress):
    with open(ETS_FILE) as groupaddresses_info:
        data = [info for info in csv.DictReader(
            groupaddresses_info) if groupaddress in info.get('Address')]

    info = data[0]

    return {
        'groupaddress': info.get('Address'),
        'groupaddress name': info.get('Group name'),
        'datapoint type': info.get('DatapointType')
    }


class DBActions(object):

    def monitor_status_save(frame):
        groupaddress = get_groupaddress(frame).get('formatted')
        info = get_groupaddress_info(groupaddress)
        status = get_value(frame, info.get("datapoint type")).get('formatted')
        post_data={
            "groupaddress_name": info.get("groupaddress name"),
            "groupaddress": groupaddress,
            "datapoint_type": info.get("datapoint type"),
            "status":  status,
        }

        try:
            requests.post(POST_MONITOR_URL, data=post_data)

        except:
            logging.warning(f"Could not save data = { post_data }")
            logging.warning(f"from URL = { POST_STATUS_URL }")

    def status_save(frame):
        groupaddress = get_groupaddress(frame).get('formatted')
        info = get_groupaddress_info(groupaddress)
        status = get_value(frame, info.get("datapoint type")).get('formatted')
        post_data={
            "groupaddress_name": info.get("groupaddress name"),
            "groupaddress": groupaddress,
            "status":  status,
        }

        try:
            requests.post(POST_STATUS_URL, data=post_data)

        except:
            logging.warning(f"Could not save data = { post_data }")
            logging.warning(f"from URL = { POST_STATUS_URL }")
