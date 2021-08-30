''' Main programm for reading knx bus traffic'''
import serial
from datetime import datetime
import logging

import knx_monitor as mon
from knx_monitor import DBActions

DEVICE = '/dev/ttyAMA0'
BAUDRATE = 19200
CHARACTER_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_EVEN
STARTBYTE = b'\x68'
STOPBYTE = b'\x16'


def main():
    with serial.Serial(DEVICE, BAUDRATE, CHARACTER_SIZE, PARITY) as connection:
        while True:
            # read frame
            connection.read_until(STARTBYTE)
            frame = bytearray(STARTBYTE)
            frame.extend(connection.read_until(STOPBYTE))

            groupaddress = mon.get_groupaddress(frame).get('formatted')
            groupaddress_info = mon.get_groupaddress_info(groupaddress)
            datapoint_type = groupaddress_info.get('datapoint type')

            # save status
            groupaddress_info['status'] = mon.get_value(
                frame, datapoint_type).get('formatted')
            groupaddress_info['timestamp'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')
            mon.save_status(groupaddress_info)
            DBActions.monitor_status_save(frame)
            DBActions.status_save(frame)


if __name__ == "__main__":
    main()
