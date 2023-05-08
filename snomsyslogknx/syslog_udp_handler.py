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
        self.client_mac = str(getmac.get_mac_address(ip=self.client_ip)).replace(
            ":", ""
        )
        self.client_info = SYSLOG_CLIENTS.get(self.client_ip)

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
            if self.client_info("is D735") and "ALS_VALUE" in message_item:
                ambient_light = message_item.split(":")
                als_value =  int(ambient_light[1])
                self._handle_lux_value(als_value)
                self._handle_relative_dimming(als_value)

            if message_item == "temperature:":
                temp_value_message = self.message_data[-1:]
                self._handle_celsius_value(temp_value_message)

    def _handle_lux_value(self, als_value):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        send_lux_value = self.client_info.get(
            "send lux groupaddress"
        )
        last_lux_value = knx_reader.baos_interface.read_raw_value(send_lux_value)

        if last_lux_value is not None:
            delta = round(float(abs(last_lux_value - als_value)), 2)
            max_lux_delta = self.client_info.get("max lux delta")
            if delta >= max_lux_delta:
                knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                logging.info(f"ip {self.client_ip} lux delta higher as {max_lux_delta} Lux, sending {als_value} Lux to KNX bus")
                knx_writer.baos_interface.send_value(send_lux_value, als_value)

    def _handle_relative_dimming(self, als_value):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        switch_groupaddress = self.client_info.get("switch groupaddress")
        is_on = knx_reader.baos_interface.read_raw_value(switch_groupaddress)

        if is_on:
            relative_dim_groupaddress = self.client_info.get("relative dim groupaddress")
            client_min_brightness = self.client_info.get("min brightness")
            client_max_brightness = self.client_info.get("max brightness")

            if als_value < client_min_brightness:
                knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                knx_writer.baos_interface.send_value(relative_dim_groupaddress, "increase")
                logging.info(f"{als_value} Lux at {self.client_ip} lower than in range {client_min_brightness}...{client_max_brightness} Lux. Dimming {relative_dim_groupaddress} up...")
            elif als_value > client_max_brightness:
                knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                knx_writer.baos_interface.send_value(relative_dim_groupaddress, "decrease")
                logging.info(f"{als_value} Lux at {self.client_ip} higher than in range {client_min_brightness}...{client_max_brightness} Lux. Dimming {relative_dim_groupaddress} down...")
            else:
                logging.info(f"{als_value} Lux at {self.client_ip} in range {client_min_brightness}...{client_max_brightness} Lux")
        else:
            logging.warning("Not switched on")

    def _handle_celsius_value(self, temp_value_message):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        send_celsius_groupaddress = self.client_info.get(
            "send celsius groupaddress"
        )
        last_value = knx_reader.baos_interface.read_raw_value(
            send_celsius_groupaddress
        )
        last_temp_value = round(float(last_value), 2)
        temp_value = round(float(temp_value_message[0]), 2)
        delta = round(float(abs(last_temp_value - temp_value)), 2)
        max_celsius_delta = self.client_info.get("max celsius delta")

        if delta >= max_celsius_delta:
            knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
            logging.info(
                f"ip {self.client_ip} celsius delta higher as {max_celsius_delta}°C, sending {temp_value}°C to KNX bus"
            )
            knx_writer.baos_interface.send_value(
                send_celsius_groupaddress, temp_value
            )

        else:
            logging.debug(f"ip {self.client_ip} has delta {delta}°C")
