import logging
import sys

# add current folder to the system path
# sys.path.append("/usr/local/snom_baos_777")
sys.path.append("/knx")
from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.INFO)

USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    while True:
        monitor = baos_ws.MonitorWebsocket(USERNAME, PASSWORD)
        interface = monitor.baos_interface
        logging.info(f"Datapoints information:\n{interface.datapoints_information}")
        logging.info(
            f"Running {monitor.ws.__class__.__name__} forever:\nId {id(monitor.ws)}\nToken: {monitor.token}\n"
        )
        monitor.ws.run_forever(
            ping_interval=60, ping_timeout=2, ping_payload="keep alive"
        )
        logging.error("Unable to login while creating KNX monitor. Trying again...")
