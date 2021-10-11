import requests
import logging


FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

def send_data(client_handle, device_id, data):
    """Sends RAW <data> to <device_id>

    All ULE expansion boards are configured to have a Unit 3 which will accept
    any message payload. Send anything you want.
    """
    # send raw data to Unit 3 (ULEasy)
    cookie = client_handle.fun_msg(

        ### Message network layer:
        src_dev_id=0,
        src_unit_id=2, #unit id of concentrator = 0x02
        dst_dev_id=device_id,
        # dst_unit_id=3,  # ULEasy unit
        dst_unit_id=1,

        ### Message transport layer:
        # reserved for future

        ### Message application layer:
        msg_type = 1, # command type
        interface_type=1,  # server
        #interface_type=0x01,  # client (destination when message type =  command)
        # interface_id=0x7f16,  # ULeasy interface
        interface_id=512,  
        interface_member=3,
        data="",
    )

    return cookie

"""callback handlers"""

def handle_fun_msg(client, msg):
    device_id = int(msg.params["SRC_DEV_ID"])
    unit_id = int(msg.params["SRC_UNIT_ID"])
    interface_id = int(msg.params["INTRF_ID"])
    data = msg.data
    logging.info(msg.data)

    if unit_id == 0 and interface_id == 0x0115:
        # device management unit, keep-alive interface
        logging.info("Device {}: keep alive".format(device_id))

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
        logging.info("Device {}: message from smoke unit".format(device_id))

    if unit_id == 3:
        # ULEasy unit (raw data)
        data = msg.data.decode("utf-8")
        logging.info("Device {}: message from raw data unit: '{}'".format(device_id, data))


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

    if len(argv) == 3:
        _, device_id, user_data = argv
    else:
        print("send requires a device ID and data")
        return

    try:
        device_id = int(device_id)
    except ValueError:
        logging.info(f"The device ID ({ device_id }) has to be a number")
        return

    send_data(client_handle, device_id, user_data)
    logging.info(f"Device { device_id }: message data { user_data } has been queued for delivery ...")
