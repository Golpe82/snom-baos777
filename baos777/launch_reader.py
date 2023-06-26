import logging
import sys

# add current folder to the system path
# sys.path.append("/usr/local/gateway")
sys.path.append("/knx")
from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.INFO)

USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    reader = None

    while True:
        if not reader:
            logging.error("No token. Creating KNX reader...")
            reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
            interface = reader.baos_interface
            logging.info(f"Datapoints information:\n{interface.datapoints_information}")
            logging.info(
                f"\nAvailable groupaddresses to read:\n{interface.sending_groupaddresses}"
            )
