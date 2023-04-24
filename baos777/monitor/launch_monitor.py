import logging
import sys

# add current folder to the system path
sys.path.append(".")
from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.DEBUG)

USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    while True:
        baos_ws.MonitorWebsocket(USERNAME, PASSWORD)
        logging.error("Unable to login while creating KNX monitor. Trying again...")
