import logging
import argparse
import time
import baos777.baos_websocket as baos_ws

parser = argparse.ArgumentParser(description='Blink KNX groupaddress (DPT1)')
parser.add_argument('groupaddress', metavar='GA', type=str,
                    help='KNX groupaddress to blink')
parser.add_argument('seconds_for_on', metavar='on (sec)', type=int,
                    help='time in seconds for on status')
parser.add_argument('seconds_for_off', metavar='off (sec)', type=int,
                    help='time in seconds for off status')
parser.add_argument('user', metavar='username', type=str,
                    help='Username for BAOS 777')
parser.add_argument('passwd', metavar='password', type=str,
                    help='Password for BAOS 777')

args = parser.parse_args()

try:
    writer = baos_ws.KNXWriteWebsocket(args.user, args.passwd)
except Exception:
    logging.error("not able to create a KNX write object")
else:
    logging.info(f"Starting to blink groupaddress {args.groupaddress}")

    while True:
        writer.baos_interface.send_value(args.groupaddress, "on")
        time.sleep(args.seconds_for_on)
        writer.baos_interface.send_value(args.groupaddress, "off")
        time.sleep(args.seconds_for_off)