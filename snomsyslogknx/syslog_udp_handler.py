import logging
import socketserver
import sys

import getmac

from syslog_clients import SYSLOG_CLIENTS

# add current folder to the system path
sys.path.append(".")

from baos777 import baos_websocket as baos_ws

USERNAME, PASSWORD = "admin", "admin"
# TODO: REFACTOR

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        logging.basicConfig(level=logging.INFO)
        self.client_ip = self.client_address[0]
        self.client_mac = str(getmac.get_mac_address(ip=self.client_ip)).replace(":", "")
        self.client_info = SYSLOG_CLIENTS.get(self.client_ip)
        # self.als_value =  None

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

            if message_item == "temperature:":
                send_celsius_groupaddress = self.client_info.get("send celsius groupaddress")
                temp_value_message = self.message_data[-1:]
                temp_value = round(float(temp_value_message[0]), 2)
                knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                logging.info(f"Sending {temp_value}°C to KNX from ip {self.client_ip}")
                knx_writer.baos_interface.send_value(send_celsius_groupaddress, temp_value)
                
