import requests
import logging

from han_fun_interfaces import InterfaceTypes, OnOff


FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


# Actions

def send_data(client_handle, device_id, data):
    cookie = client_handle.fun_msg(
        ### Message network layer:
        src_dev_id=0x00,
        src_unit_id=0x02, #unit id of concentrator = 0x02
        dst_dev_id=device_id,
        dst_unit_id=0x01,

        ### Message transport layer:
        # reserved for future

        ### Message application layer:
        msg_type = 0x01, # command type
        interface_type=InterfaceTypes.SERVER.value,
        interface_id=OnOff.IFACE_ID.value,  
        interface_member=OnOff.TOGGLE.value,
        data="",
    )

    return cookie

# callback handlers

def handle_fun_msg(client, msg):
    device_id = int(msg.params["SRC_DEV_ID"])
    unit_id = int(msg.params["SRC_UNIT_ID"])
    interface_id = int(msg.params["INTRF_ID"])
    data = msg.data
    logging.info(msg.data)

    if unit_id == 0 and interface_id == 0x0115:
        # device management unit, keep-alive interface
        logging.info(f"Device { device_id }: keep alive")

    if unit_id == 1:
        # voice call unit
        if msg.data[5]:
            logging.info("open")
            requests.get("http://192.168.178.47:1234/1/2/10-an")
            send_data(client, 2, 3)
        else:
            logging.info("close")
            requests.get("http://192.168.178.47:1234/1/2/10-aus")
            send_data(client, 2, 3)
        logging.info(f"Device { device_id }: message from voice call unit")

    if unit_id == 2:
        # smoke unit
        logging.info(f"Device { device_id }: message from smoke unit")

    if unit_id == 3:
        # ULEasy unit (raw data)
        data = msg.data.decode("utf-8")
        logging.info(f"Device { device_id }: message from raw data unit: '{ data }'")


# console commands

def send_user_data(client_handle, argv):
    """
    NAME
    send - send a string to a device

    SYNOPSIS
    send device_id data_string

    DESCRIPTION
    Send a character string from the hub to the specified device. The string
    must not contain spaces. Returns a fail if the specified device is not
    registered.
    """
    all_arguments = len(argv) == 3

    if all_arguments:
        _, device_id, user_data = argv
    else:
        logging.error("send requires a device ID and data")
        return

    try:
        device_id = int(device_id)
    except ValueError:
        logging.info(f"The device ID ({ device_id }) must be a number")
        return

    send_data(client_handle, device_id, user_data)
    logging.info(f"Device { device_id }: message data { user_data } has been queued for delivery ...")
