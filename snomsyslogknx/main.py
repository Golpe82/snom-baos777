import socketserver
import sys

from syslog_udp_handler import SyslogUDPHandler
# add current folder to the system path
sys.path.append(".")
from baos777 import baos_websocket as baos_ws

HOST, PORT = "0.0.0.0", 514
USERNAME = "admin"
PASSWORD = "admin"

if __name__ == "__main__":
    try:
        # knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
        # knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever()
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("\nCrtl+C Pressed. Shutting down.")
