import logging
import socketserver

import getmac

from snom_syslog_parser import KNXActions, DBActions, to_lux
from syslog_clients import SYSLOG_CLIENTS

logging.basicConfig(level=logging.INFO, format='%(message)s', datefmt='', filemode='a')

# TODO: REFACTOR

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.client_ip = self.client_address[0]
        self.client_mac = str(getmac.get_mac_address(ip=self.client_ip)).replace(":", "")
        self.client_info = SYSLOG_CLIENTS.get(self.client_ip)
        self.knx_action = KNXActions(self.client_info)
        self.database_actions = DBActions()
        self.als_value =  None
        self.temp_value = None
        logging.info(self.client_mac)

    def handle(self):
        for message_item in self.message_data:
            if "ALS_VALUE" in message_item:
                ambient_light = message_item.split(":")
                self.als_value =  int(ambient_light[1])
                self.database_actions.als_save(self.client_ip, self.client_mac, self.als_value, self.lux_value)
                logging.info(f"{self.client_info.get('label')}: {self.lux_value} lux")

                if self.knx_action.get_status() == "on":
                    self.knx_action.knx_dimm_relative(self.lux_value)
                else:
                    logging.warning("Not switched on")

            elif message_item == "usb_temperature_event:":
                temp_value_message = self.message_data[-1:]
                temp_value = temp_value_message[0]
                self.temp_value = temp_value[:5]
                logging.info(f"{self.temp_value[:5]}°C")
                self.knx_action.knx_send_celsius(self.temp_value.split(".")[0])

    @property
    def message(self):
        raw_data = self.request[0].strip()
        return str(bytes.decode(raw_data))

    @property
    def message_data(self):
        return self.message.split()

    @property
    def lux_value(self):
        return to_lux(self.als_value)