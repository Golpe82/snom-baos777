import requests
import logging


FORMAT = '%(asctime)s:%(levelname)s:%(message)s'
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

class SnomHANHandlers(object):
    """callback handlers"""

    def handle_fun_msg(self, client, msg):
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
            else:
                logging.info("close")
                requests.get("http://192.168.178.47:1234/1/2/10-aus")
            logging.info(f"Device { device_id }: message from voice call unit")

        if unit_id == 2:
            # smoke unit
            logging.info("Device {}: message from smoke unit".format(device_id))

        if unit_id == 3:
            # ULEasy unit (raw data)
            data = msg.data.decode("utf-8")
            logging.info("Device {}: message from raw data unit: '{}'".format(device_id, data))