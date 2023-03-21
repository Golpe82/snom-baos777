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

    def status_save(frame):
        groupaddress = get_groupaddress(frame).get("formatted")
        if groupaddress == "1/2/20":
            logging.error("-----Incoming knx telegram----")
            # frame[OctectIndex.MESSAGE_CODE] == MessageCode.L_DATA_IND

            for idx, byte in enumerate(frame):
                if idx == 5:
                    logging.error(f"Byte {idx}: {hex(byte)}")
                    logging.error(f"{hex(frame[OctectIndex.MESSAGE_CODE])}")
            logging.error("-----")

        info = get_groupaddress_info(groupaddress)
        datapointtype  = info.get("datapoint type")
        is_dpt1 = "DPT-1" in datapointtype or "DPST-1" in datapointtype

        # save only dpt1 otherwise too much to save
        if is_dpt1:
            status = get_value(frame, datapointtype).get("formatted")
            logging.info(f"saving status {status} for groupaddress {groupaddress} with dpt {datapointtype}")

            # if groupaddress == BLIND_GROUPADDRESS:
            #     DECTULEActions().control_blind(status)

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
