''' main programm for monitoring knx bus traffic'''
import serial

import knx_monitor as mon


def main():
    with serial.Serial(
        mon.KnxSerial.DEVICE, mon.KnxSerial.BAUDRATE, mon.KnxSerial.CHARACTER_SIZE, mon.KnxSerial.PARITY
    ) as connection:

        while True:
            connection.read_until(BytesValues.STARTBYTE)
            frame = bytearray(BytesValues.STARTBYTE)
            frame.extend(connection.read_until(BytesValues.STOPBYTE))

            groupaddress = mon.get_groupaddress(frame).get('formatted')
            groupaddress_info = mon.get_groupaddress_info(groupaddress)
            datapoint_type = groupaddress_info.get('datapoint type')
            groupaddress_info['status'] = mon.get_value(
                frame, datapoint_type).get('formatted')
            groupaddress_info['timestamp'] = datetime.now().strftime(
                '%Y-%m-%d %H:%M:%S')
            save_status(groupaddress_info)


if __name__ == "__main__":
    main()
