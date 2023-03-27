""" Main programm for reading knx bus traffic"""
import serial
import logging
import binascii
import requests

import knx_monitor

DEVICE = "/dev/ttyAMA0"
BAUDRATE = 19200
CHARACTER_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_EVEN
STARTBYTE = b"\x68"
STOPBYTE = b"\x16"

logging.basicConfig(level=logging.DEBUG)

def main():
    with serial.Serial(DEVICE, BAUDRATE, CHARACTER_SIZE, PARITY) as connection:
        telegram_old = b"\xFF"
        while True:
            # read frame
            connection.read_until(STARTBYTE)
            telegram = bytearray(STARTBYTE)
            telegram.extend(connection.read_until(STOPBYTE))
            logging.info(f"Incoming ft1.2 telegram: {binascii.hexlify(telegram)}")

            if telegram[knx_monitor.OctectIndex.MESSAGE_CODE] == knx_monitor.MessageCode.L_DATA_CON:
                groupaddress = knx_monitor.get_groupaddress(telegram).get("formatted")
                logging.info(f"for groupaddress {groupaddress}")
                datapoint_type = knx_monitor.get_groupaddress_info(groupaddress).get("datapoint type")
                value = knx_monitor.get_value(telegram, datapoint_type).get("formatted")
                logging.info(f"with value {value}")

                if telegram_old != telegram:
                    knx_gateway = "localhost:8000"
                    logging.error("update led subscriptors")
                    requests.get(f"http://{knx_gateway}/knx/update_led_subscriptors/{groupaddress}/{value}")

                    #knx_monitor.DBActions.monitor_status_save(telegram)
                    knx_monitor.DBActions.status_save(telegram)
                    telegram_old = telegram


if __name__ == "__main__":
    main()
