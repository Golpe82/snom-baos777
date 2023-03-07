""" Main programm for reading knx bus traffic"""
import serial
import logging

from knx_monitor import DBActions

DEVICE = "/dev/ttyAMA0"
BAUDRATE = 19200
CHARACTER_SIZE = serial.EIGHTBITS
PARITY = serial.PARITY_EVEN
STARTBYTE = b"\x68"
STOPBYTE = b"\x16"

logging.basicConfig(level=logging.DEBUG)


def main():
    with serial.Serial(DEVICE, BAUDRATE, CHARACTER_SIZE, PARITY) as connection:
        while True:
            # read frame
            connection.read_until(STARTBYTE)
            frame = bytearray(STARTBYTE)
            frame.extend(connection.read_until(STOPBYTE))
            # not in use, too much traffic:
            # DBActions.monitor_status_save(frame)
            DBActions.status_save(frame)


if __name__ == "__main__":
    main()
