'''Module for reading telegrams from KNX bus'''
import os
import re
import csv
import requests
import logging

import datapoint_types


ETS_FILE = '/usr/local/gateway/iot/knx/media/ga.csv'
STATI_FILE = '/usr/local/gateway/knxmonitor/KNX_stati.csv'
DEST_HIGH_BYTE = 11
DEST_LOW_BYTE = 12
PAYLOAD = {
    'Byte0': 15,
    'Byte1': 16,
}


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


def create_stati_file(groupaddress_info):
    with open(STATI_FILE, "w", newline="") as write_stati:
        stati = csv.DictWriter(
            write_stati, fieldnames=groupaddress_info.keys())
        stati.writeheader()
        stati.writerow(groupaddress_info)


def update_stati_file(groupaddress_info):
    with open(STATI_FILE, newline="") as read_stati:
        stati = [status for status in csv.DictReader(read_stati)]
        found = False
        new_status = {}

        for index, raw in enumerate(stati):
            if groupaddress_info.get('groupaddress') in stati[index]['groupaddress']:
                stati[index]['status'] = groupaddress_info.get('status')
                found = True
                break

        if not found:
            new_status = groupaddress_info

    with open(STATI_FILE, "w", newline="") as update_stati:
        writer = csv.DictWriter(
            update_stati, fieldnames=groupaddress_info.keys())
        writer.writeheader()
        writer.writerows(stati)

        if new_status:
            writer.writerow(new_status)


def save_status(groupaddress_info):
    if os.path.isfile(STATI_FILE):
        update_stati_file(groupaddress_info)

    else:
        create_stati_file(groupaddress_info)


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

def get_status(groupaddress):
    status = None

    with open(STATI_FILE) as knx_stati:
        while True:
            address_info = knx_stati.readline()

            if not address_info:
                break

            if groupaddress in address_info:
                status = address_info.split(",")[3]

    return status

POST_MONITOR_URL = "http://localhost:8000/knx/groupaddress_monitor"
POST_STATUS_URL = "http://localhost:8000/knx/status"

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
