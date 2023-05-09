import logging
import json
import requests
import socketserver
import sys

import getmac

# add current folder to the system path
sys.path.append("/usr/local/gateway")

from baos777 import baos_websocket as baos_ws

USERNAME, PASSWORD = "admin", "admin"
AMBIENT_LIGHT_RELATIONS_URL = "http://localhost:8000/admin/knx/ambientlightrelation/"
TEMPERATURE_RELATIONS_URL = "http://localhost:8000/admin/knx/temperaturerelation/"
# TODO: REFACTOR

class SyslogUDPHandler(socketserver.BaseRequestHandler):
    def setup(self):
        logging.basicConfig(level=logging.INFO)
        self.client_ip = self.client_address[0]
        source_mac_address = str(getmac.get_mac_address(ip=self.client_ip))
        self.client_mac = source_mac_address.replace(":", "")

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
            if "ALS_VALUE" in message_item:
                response = requests.get(f"http://localhost:8000/knx/relations/ambient_light/ips/")
                als_relation_ips = json.loads(response.text)

                if self.client_ip in als_relation_ips:
                    try:
                        response = requests.get(f"http://localhost:8000/knx/relations/ambient_light/{self.client_ip}/")
                        response.raise_for_status()
                    except requests.exceptions.HTTPError:
                        logging.error(response.status_code)
                        logging.error(f"has {self.client_ip} ambient light relations?\n Check it here: {AMBIENT_LIGHT_RELATIONS_URL}")
                    else:
                        ambient_light = message_item.split(":")
                        als_value =  int(ambient_light[1])
                        als_relation = json.loads(response.text)
                        self._handle_lux_value(als_relation, als_value)
                        self._handle_relative_dimming(als_relation, als_value)

            if message_item == "temperature:":
                response = requests.get(f"http://localhost:8000/knx/relations/temperature/ips/")
                temp_relations_ips = json.loads(response.text)
                logging.info(temp_relations_ips)

                if self.client_ip in temp_relations_ips:
                    try:
                        response = requests.get(f"http://localhost:8000/knx/relations/temperature/{self.client_ip}/")
                        response.raise_for_status()
                    except requests.exceptions.HTTPError:
                        logging.error(response.status_code)
                        logging.error(f"has {self.client_ip} temperature relations?\n Check it here: {TEMPERATURE_RELATIONS_URL}")
                    else:
                        temp_value_message = self.message_data[-1:]
                        temperature_relation = json.loads(response.text)
                        self._handle_celsius_value(temperature_relation, temp_value_message)

    def _handle_lux_value(self, als_relation, als_value):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        send_lux_value = als_relation.get("send lux groupaddress")
        last_lux_value = knx_reader.baos_interface.read_raw_value(send_lux_value)

        if last_lux_value is not None:
            delta = round(float(abs(last_lux_value - als_value)), 2)
            max_lux_delta = als_relation.get("lux delta")
            if delta >= max_lux_delta:
                knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                logging.info(f"ip {self.client_ip} lux delta higher as {max_lux_delta} Lux, sending {als_value} Lux to KNX bus")
                knx_writer.baos_interface.send_value(send_lux_value, als_value)

    def _handle_relative_dimming(self, als_relation, als_value):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        switch_groupaddress = als_relation.get("switch groupaddress")
        is_on = knx_reader.baos_interface.read_raw_value(switch_groupaddress)

        if is_on:
            relative_dim_groupaddress = als_relation.get("dimm groupaddress")
            client_min_brightness = als_relation.get("min lux value")
            client_max_brightness = als_relation.get("max lux value")

            if als_value < client_min_brightness:
                brightness_status_address = als_relation.get("dimm status groupaddress")
                brightness_status = knx_reader.baos_interface.read_value(brightness_status_address)
                logging.error(brightness_status)

                if brightness_status != "100%":
                    knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                    knx_writer.baos_interface.send_value(relative_dim_groupaddress, "increase")
                    logging.info(f"{als_value} Lux at {self.client_ip} lower than {client_min_brightness} Lux. Dimming {relative_dim_groupaddress} up...")
                else:
                    logging.info(f"Should dimm up, but address {brightness_status_address} has already maximum value")

            elif als_value > client_max_brightness:
                brightness_status_address = als_relation.get("dimm status groupaddress")
                brightness_status = knx_reader.baos_interface.read_value(brightness_status_address)

                if brightness_status != "0%":
                    knx_writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
                    knx_writer.baos_interface.send_value(relative_dim_groupaddress, "decrease")
                    logging.info(f"{als_value} Lux at {self.client_ip} higher than {client_max_brightness} Lux. Dimming {relative_dim_groupaddress} down...")
                else:
                    logging.info(f"Should dimm down, but address {brightness_status_address} has already minimum value")
            else:
                logging.debug(f"{als_value} Lux at {self.client_ip} in range {client_min_brightness}...{client_max_brightness} Lux")
        else:
            logging.debug("Not switched on")

    def _handle_celsius_value(self, temperature_relation, temp_value_message):
        knx_reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
        send_celsius_groupaddress = temperature_relation.get("send celsius groupaddress")
        last_value = knx_reader.baos_interface.read_raw_value(
            send_celsius_groupaddress
        )

        if last_value is not None:
            last_temp_value = round(float(last_value), 2)
            temp_value = round(float(temp_value_message[0]), 2)
            delta = round(float(abs(last_temp_value - temp_value)), 2)
            max_celsius_delta = temperature_relation.get("celsius delta")

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
