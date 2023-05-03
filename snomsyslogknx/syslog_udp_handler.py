import logging
import socketserver
import sys
from time import sleep

import getmac

from syslog_actions import KNXActions, DBActions
from syslog_clients import SYSLOG_CLIENTS

# add current folder to the system path
sys.path.append(".")
from baos777 import baos_websocket as baos_ws

logging.basicConfig(level=logging.DEBUG)

USERNAME = "admin"
PASSWORD = "admin"
# TODO: REFACTOR

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        self.client_ip = self.client_address[0]
        logging.debug(self.client_ip)
        self.client_mac = str(getmac.get_mac_address(ip=self.client_ip)).replace(":", "")
        logging.debug(self.client_mac)
        self.client_info = SYSLOG_CLIENTS.get(self.client_ip)
        # self.knx_action = KNXActions(self.client_info)
        # self.knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
        # self.knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        #self.database_actions = DBActions()
        self.als_value =  None
        self.temp_value = None

    @property
    def message(self):
        raw_data = self.request[0].strip()
        return str(bytes.decode(raw_data))

    @property
    def message_data(self):
        return self.message.split()

    @property
    def lux_value(self):
        value = int(self.als_value) * 6.5 / 100

        return round(value, 2)

    def handle(self):
        for message_item in self.message_data:
            # if "ALS_VALUE" in message_item:
            #     switch_groupaddress = self.client_info.get("switch groupaddress")
            #     ambient_light = message_item.split(":")
            #     self.als_value =  int(ambient_light[1])
            #     #self.database_actions.als_save(self.client_ip, self.client_mac, self.als_value, self.lux_value)
            #     logging.info(f"{self.client_info.get('label')}: {self.lux_value} lux")

            #     # if self.knx_action.get_groupaddress_status(switch_groupaddress) == "on":
            #     if self.knx_reader.baos_interface.read_value(switch_groupaddress):
            #         relative_dim_groupaddress = self.client_info.get("relative dim groupaddress")
            #         client_min_brightness = self.client_info.get("min brightness")
            #         client_max_brightness = self.client_info.get("max brightness")
            #         if self.als_value < client_min_brightness:
            #             self.knx_writer.baos_interface.send_value(relative_dim_groupaddress, "increase")
            #         elif self.als_value > client_max_brightness:
            #             self.knx_writer.baos_interface.send_value(relative_dim_groupaddress, "decrease")
            #         sleep(10)
            #         logging.info(f"{self.knx_reader.baos_interface.read_value('5/1/25')}%")
            #         # relative_dim_groupaddress = self.client_info.get("relative dim groupaddress")
                    
            #         # self.knx_action.knx_dimm_relative(relative_dim_groupaddress, self.lux_value)
            #     else:
            #         logging.warning("Not switched on")

            # elif message_item == "temperature:":
            logging.info(message_item)
            if message_item == "temperature:":
                send_celsius_groupaddress = self.client_info.get("send celsius groupaddress")
                temp_value_message = self.message_data[-1:]
                temp_value = temp_value_message[0]
                self.temp_value = temp_value[:5]
                logging.info(f"{self.temp_value[:5]}°C")
                sleep(10)
                #self.knx_action.knx_send_celsius(send_celsius_groupaddress, self.temp_value.split(".")[0])
