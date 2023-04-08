"""Module for reading telegrams from KNX bus"""
import re
import csv
import requests
import logging

import datapoint_types
from dect_ule_actions import DECTULEActions, BLIND_GROUPADDRESS


ETS_FILE = "/usr/local/gateway/iot/knx/media/ga.csv"

PAYLOAD = {
    "Byte0": 15,
    "Byte1": 16,
}
POST_MONITOR_URL = "http://localhost:8000/knx/groupaddress_monitor"
POST_STATUS_URL = "http://localhost:8000/knx/status"


class OctectIndex:
    FT12_STARTBYTE = 0
    FT12_LENGTH = 1
    MESSAGE_CODE = 5
    DEST_HIGH = 11
    DEST_LOW = 12
    PAYLOAD_LENGTH = 13

class MessageCode:
    L_DATA_REQ = 0x11
    L_DATA_CON = 0x2E
    L_DATA_IND = 0x29

logging.basicConfig(level=logging.DEBUG)


def get_groupaddress(frame):
    raw_address = f"{frame[OctectIndex.DEST_HIGH]} { frame[OctectIndex.DEST_LOW] }"
    subaddress = frame[OctectIndex.DEST_LOW]
    high_byte = frame[OctectIndex.DEST_HIGH]
    midaddress_mask = 0x07
    midaddress = high_byte & midaddress_mask
    mainaddress = high_byte >> 0x03

    groupaddress = f"{ mainaddress }/{ midaddress }/{ subaddress }"

    return {
        "raw": raw_address,
        "formatted": groupaddress,
        }


def get_value(frame, datapoint_type):
    logging.info(f"datapoint {datapoint_type}")
    if datapoint_type == "DPST-5-1":
        raw_value = frame[PAYLOAD.get("Byte1")]
    else:
        raw_value = frame[PAYLOAD.get("Byte0")]
    value = ""

    for dpt, pattern in datapoint_types.PATTERNS.items():
        if re.match(pattern, datapoint_type):
            handler = datapoint_types.DptHandlers(raw_value)
            value = handler.get_formatted_value(dpt)

    return {"raw": raw_value, "formatted": value}


def get_groupaddress_info(groupaddress):
    logging.info(f"Searching for {groupaddress} in ETS file")

    with open(ETS_FILE) as groupaddresses_info:
        fieldnames = [
            "Group name",
            "Address",
            "Central",
            "Unfiltered",
            "Description",
            "DatapointType",
            "Security",
        ]
        data = [
            info
            for info in csv.DictReader(groupaddresses_info, fieldnames=fieldnames)
            if groupaddress in info.get("Address")
        ]

    try:
        info = data[0]
        return {
            "groupaddress": info.get("Address"),
            "groupaddress name": info.get("Group name"),
            "datapoint type": info.get("DatapointType"),
        }
    except IndexError:
        logging.exception(f"Groupaddress {groupaddress} not found in ETS file")
        return {
            "groupaddress": "",
            "groupaddress name": "",
            "datapoint type": "",   
        }


def to_string(frame):
    return "x".join([format(byte, "X").zfill(2) for byte in frame])


class DBActions(object):

    ID_2_GROUPADDRESS = {
                "1": "3/1/10",
                "2": "3/1/11",
                "3": "4/1/0",
            }

    # not in use, too much traffic:
    def monitor_status_save(frame):
        logging.info(f"debugging mon frame {frame}")
        logging.info(f"debugging mon unformatted {get_groupaddress(frame)}")

        groupaddress = get_groupaddress(frame).get("formatted")
        info = get_groupaddress_info(groupaddress)
        status = get_value(frame, info.get("datapoint type")).get("formatted")
        post_data = {
            "groupaddress_name": info.get("groupaddress name"),
            "groupaddress": groupaddress,
            "datapoint_type": info.get("datapoint type"),
            "status": status,
            "raw_frame": to_string(frame),
        }

        try:
            requests.post(POST_MONITOR_URL, data=post_data)

        except Exception:
            logging.warning(f"Could not save data = { post_data }")
            logging.warning(f"from URL = { POST_MONITOR_URL }")

    def get_groupaddress_777(id):
        # look up group address via 777 id
        groupaddress = DBActions.ID_2_GROUPADDRESS.get(str(id))
        if groupaddress is not None:
            return {
                #"raw": '',
                "formatted": groupaddress,
                }

    def get_value_and_groupaddress_777(message):
        # DPT might be unknown yet, make sure we return an error value instead
        value_formatted = 'UNDEFINED'

        message = message['indications']
        type = message["type"] 
        if type == 'datapoint_ind':

            # a list of values could be returned. We use the last entry in the list. 
            value_list = message['values']
            for element in value_list:
                dpt = element['Format']
                id = element['id']
                gaddr = DBActions.get_groupaddress_777(str(id))
                state = element['state']

                logging.info(f"datapoint {dpt}")

                # DPT already comes in clear text  
                if dpt == "DPT1":
                    value = element['value']
                    value_formatted = "On" if value else "Off"
                # different call to handler - get formatted ?

                #handler = datapoint_types.DptHandlers(raw_value)
                #value = handler.get_formatted_value(dpt)
            return {"groupaddress": gaddr, "DPT": dpt, "value_formatted": value_formatted}

    def monitor_status_save_777(message):
        logging.info(f"debugging mon message {message}")

        result = DBActions.get_value_and_groupaddress_777(message)

        groupaddress = result['groupaddress']['formatted']
        dpt = result['DPT']
        #info = get_groupaddress_info(groupaddress)

        status = result['value_formatted']
        post_data = {
            #"groupaddress_name": info.get("groupaddress name"),
            "groupaddress": groupaddress,
            "datapoint_type": dpt,
            "status": status,
            "raw_frame": '',
        }

        try:
            requests.post(POST_MONITOR_URL, data=post_data)

        except Exception:
            logging.warning(f"Could not save data = { post_data }")
            logging.warning(f"from URL = { POST_MONITOR_URL }")

    def status_save(frame):
        groupaddress = get_groupaddress(frame).get("formatted")
        info = get_groupaddress_info(groupaddress)
        datapointtype  = info.get("datapoint type")
        is_dpt1 = "DPT-1" in datapointtype or "DPST-1" in datapointtype

        # save only dpt1 otherwise too much to save
        if is_dpt1:
            status = get_value(frame, datapointtype).get("formatted")
            logging.info(f"saving status {status} for groupaddress {groupaddress} with dpt {datapointtype}")

            knx_gateway = "localhost:8000"
            logging.error("update led subscriptors")
            requests.get(f"http://{knx_gateway}/knx/update_led_subscriptors/{groupaddress}/{status}")

            post_data = {
                "groupaddress_name": info.get("groupaddress name"),
                "groupaddress": groupaddress,
                "status": status,
            }

            try:
                requests.post(POST_STATUS_URL, data=post_data)

            except Exception:
                logging.warning(f"Could not save data = { post_data }")
                logging.warning(f"from URL = { POST_STATUS_URL }")
