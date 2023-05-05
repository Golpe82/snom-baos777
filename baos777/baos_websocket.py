"""It creates a BAOS websocket connection"""

from abc import ABC, abstractmethod
import logging
import json
from http import HTTPStatus

import requests
import websocket
import sys

# add current folder to the system path
sys.path.append("/usr/local/gateway")

from baos777.http_handler import HTTPHandler
from baos777.baos777_interface import BAOS777Interface
from baos777.baos_indication_message import BAOSIndicationsMessage
from baos777.datapoint_values import DPT1_VALUES
from baos777 import utils

logging.basicConfig(level=logging.INFO)

if logging.getLogger().level == logging.DEBUG:
    websocket.enableTrace(True)


# KNX_GATEWAY = "10.110.16.59:8000"
# BAOS777_IP = "10.110.16.63"
KNX_GATEWAY = "192.168.178.47:8000"
BAOS777_IP = "192.168.178.41"


class BaseWebsocket(ABC):
    def __init__(self, username, password):
        self.ws = None
        self.user = username
        self.pswd = password
        self.token = None
        self.baos_interface = None
        self.incoming_message = None
        self._login()
        self._connect()

    def _login(self):
        login_url = f"http://{BAOS777_IP}/rest/login"
        credentials = {"password": self.pswd, "username": self.user}

        try:
            response = requests.post(login_url, json=credentials)

            if response.status_code != HTTPStatus.OK:
                raise response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logging.error(
                f"\nUnable to authenticate BAOS 777 websocket!:\n\tBAOS returned: {response.text}\n\tfor HTTP code {response.status_code}\n"
            )
            http_handler = HTTPHandler(self, response, credentials)
            http_handler.handle(exception=e)

        except requests.exceptions.ConnectionError:
            logging.error("BAOS 777 not reachable, ConnectionError.")

        else:
            self._set_token(response.text)
            logging.info(
                f"Logged into BAOS 777. Token {self.token}"
            )

    def _set_token(self, token):
        # must be really longer than 10?
        if len(token) <= 10:
            raise Exception(f"Token length < 10: {token}")

        self.token = token

    def _connect(self):
        websocket_host = f"ws://{BAOS777_IP}/websocket"
        websocket_url = f"{websocket_host}?token={self.token}"

        try:
            self.ws = websocket.WebSocketApp(
                websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
        except Exception:
            logging.exception("BAOS Webservice down, try reconnect")

        self.baos_interface = BAOS777Interface(self.token)

    @abstractmethod
    def on_message(self, ws, message):
        ...

    @abstractmethod
    def on_open(self, ws):
        ...

    def on_error(self, ws, error):
        logging.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(
            f"\nClosing conection:\nWebsocket id {id(self.ws)}\nToken {self.token}"
        )
        self.ws.close()
        self.ws.keep_running = False


class MonitorWebsocket(BaseWebsocket):
    def on_open(self, ws):
        logging.info(
            f"\nOpened KNX monitor connection:\nWebsocket id {id(self.ws)}\nToken {self.token}"
        )

    def on_message(self, ws, message):
        logging.info(f"BAOS event:\n{message}\n")
        self.baos_interface.baos_message = json.loads(message)
        self.incoming_message = BAOSIndicationsMessage(self.baos_interface.baos_message)
        urls_to_send = []

        for datapoint_value in self.incoming_message.values:
            datapoint_id = datapoint_value.get("id")
            datapoint_format = datapoint_value.get("Format")
            datapoint_value = datapoint_value.get("value")

            if datapoint_format == "DPT1":
                led_update_url = self._get_led_update_url(datapoint_id, datapoint_value)
                urls_to_send.append(led_update_url)
                logging.info(f"Appended url for dapoint with format {datapoint_format}")

            else:
                logging.info(
                    f"No needed action for datapoints with format {datapoint_format}"
                )

        if urls_to_send:
            utils.send_urls(urls_to_send)
        else:
            logging.info("No urls to send after BAOS 777 incoming message")

    def _get_led_update_url(self, datapoint_id, datapoint_value):
        led_update_url = f"http://{KNX_GATEWAY}/knx/update_led_subscriptors/"
        datapoint_sending_groupaddress = self.baos_interface.get_sending_groupaddress(
            datapoint_id
        )
        value = next(
            (_key for _key, _value in DPT1_VALUES.items()
            if _value == datapoint_value),
            None
        )

        return f"{led_update_url}{datapoint_sending_groupaddress}/{value}"


class KNXWriteWebsocket(BaseWebsocket):
    def on_open(self, ws):
        ...

    def on_message(self, ws, message):
        ...


class KNXReadWebsocket(BaseWebsocket):
    def on_open(self, ws):
        ...

    def on_message(self, ws, message):
        ...
