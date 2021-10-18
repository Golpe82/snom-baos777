import logging
import requests

import snom_actions as snm_actn
from han_fun_profiles import Profiles

FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG
HAN_FUN_PROFILES = Profiles.__subclasses__()

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


def handle_fun_msg(client, msg):
    device_id = int(msg.params["SRC_DEV_ID"])
    unit_id = int(msg.params["SRC_UNIT_ID"])
    interface_id = int(msg.params["INTRF_ID"])
    data = msg.data
    logging.info(msg.data)

    if unit_id == 0 and interface_id == 0x0115:
        # device management unit, keep-alive interface
        logging.info("Device %s: keep alive", device_id)

    if unit_id == 1:
        # voice call unit
        if msg.data[5]:
            logging.info("open")
            requests.get("http://192.168.178.47:1234/1/2/10-an")
            snm_actn.send_data(client, 2, "on")
        else:
            logging.info("close")
            requests.get("http://192.168.178.47:1234/1/2/10-aus")
            snm_actn.send_data(client, 2, "off")
        logging.info("Device %s: message from voice call unit", device_id)

    if unit_id == 2:
        # smoke unit
        logging.info("Device %s: message from smoke unit", device_id)

    if unit_id == 3:
        # ULEasy unit (raw data)
        data = msg.data.decode("utf-8")
        logging.info("Device %s: message from raw data unit: %s", device_id, data)

def process_rx_data(client, data_str):
    """Custom handler for the received ascii messages from the HAN server."""
    # Do something with the data received from the CMBS block.
    # This could be something received over the air or from
    # inside the CMBS block
    logging.info("HAN Client <<-- HAN Server\n" + data_str)


def handle_dev_registered(client, msg):
    device_id = int(msg.params["DEV_ID"])
    logging.info("Device {}: registered (or registration updated)".format(device_id))


def handle_reg_closed(client, msg):
    reason = msg.params["REASON"]
    logging.info("Registration window closed (reason: {})".format(reason))


def handle_fun_msg_res(client, msg):
    device_id = int(msg.params["DEV_ID"])
    logging.info("Device {}: message delivered.".format(device_id))


def handle_call_establish_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    participant = msg.params["PARTICIPANT"]
    if participant[0] == "D":
        participant = "Device {}".format(int(participant[1:]))
    else:
        participant = "Handset " + participant
    logging.info("Call {}: established with {}".format(call_id, participant))


def handle_call_dev_released_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    device_id = int(msg.params["DEV_ID"])
    logging.info("Call {}: device {} released".format(call_id, device_id))


def handle_call_release_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    logging.info("Call {}: released".format(call_id))
    pass

