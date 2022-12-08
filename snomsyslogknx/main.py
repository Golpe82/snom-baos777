import logging
import socketserver

import getmac

from snom_syslog_parser import KNXActions, DBActions, to_lux
from syslog_clients import SYSLOG_CLIENTS

HOST, PORT = "0.0.0.0", 514

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filemode='a')


class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.client_ip = self.client_address[0]
        self.client_mac = str(getmac.get_mac_address(ip=self.client_ip)).replace(":", "")
        self.client_info = SYSLOG_CLIENTS.get(self.client_ip)
        self.knx_action = KNXActions(self.client_info)
        self.database_actions = DBActions()
        logging.info(self.client_mac)

    def handle(self):
        if self.als_value:
            self.database_actions.als_save(self.client_ip, self.client_mac, self.als_value, self.lux_value)
            logging.info(f"{self.client_info.get('label')}: {self.lux_value} lux")

            if self.knx_action.get_status() == "on":
                self.knx_action.knx_dimm_relative(self.lux_value)
            else:
                logging.info(f"Not switched on")

    @property
    def message(self):
        raw_data = self.request[0].strip()
        return str(bytes.decode(raw_data))

    @property
    def message_data(self):
        return self.message.split()

    @property
    def als_value(self):
        return self.get_als_value()

    @property
    def lux_value(self):
        return to_lux(self.als_value)

    def get_als_value(self):
        for message_item in self.message_data:
            if "ALS_VALUE" in message_item:
                ambient_light = message_item.split(":")
                return int(ambient_light[1])

if __name__ == "__main__":
    try:
        server = socketserver.UDPServer((HOST,PORT), SyslogUDPHandler)
        server.serve_forever()
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print ("\nCrtl+C Pressed. Shutting down.")
