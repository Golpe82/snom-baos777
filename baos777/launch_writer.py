import logging
import sys

# add current folder to the system path
sys.path.append(".")
from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.DEBUG)

USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    writer = None
    
    while True:
        if not writer:
            logging.error("No token. Creating KNX writer...")
            writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
        #writer.baos_interface.send_value("3/1/10", "on")
