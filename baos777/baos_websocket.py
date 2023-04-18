from abc import ABC, abstractmethod
import logging
import json
from http import HTTPStatus

import requests
import websocket

from baos777.http_handler import HTTPHandler
from knxmonitor import knx_monitor

logging.basicConfig(level=logging.DEBUG)

if logging.getLogger().level == logging.DEBUG:
    websocket.enableTrace(True)


class BaseWebsocket(ABC):
    def __init__(self):
        self.token = None

    @abstractmethod
    def on_message(self, ws, message):
        ...

    def login(self, user, password):
        login_url = "http://10.110.16.63/rest/login"
        credentials = {"password": password, "username": user}

        try:
            response = requests.post(login_url, json=credentials)

            if response.status_code != HTTPStatus.OK:
                raise response.raise_for_status()

        except requests.exceptions.HTTPError as e:
            logging.error(
                f"\nUnable to authenticate BAOS 777 websocket!:\n\tBAOS returned: {response.text}\n\tfor HTTP code {response.status_code}"
            )
            http_handler = HTTPHandler(self, response, credentials)
            http_handler.handle(exception=e)

        except requests.exceptions.ConnectionError:
            logging.error("BAOS 777 not reachable, ConnectionError.")

        else:
            self.set_token(response)
            logging.info(
                f"{response.status_code}: Logged into BAOS 777 with credentials {credentials} and token {self.token}"
            )
            self.connect()
            logging.info(f"Running websocket id {id(self.ws)} forever...")

    def set_token(self, login_response):
        # must be really longer than 10?
        if len(login_response.text) <= 10:
            raise Exception(f"Token length < 10: {login_response.text}")

        logging.info(f"New BAOS token: {login_response.text}")
        self.token = login_response.text

    def connect(self):
        websocket_host = "ws://10.110.16.63/websocket"
        websocket_url = f"{websocket_host}?token={self.token}"

        try:
            logging.info(f"trying to connect to {websocket_url}")
            self.ws = websocket.WebSocketApp(
                websocket_url,
                on_open=self.on_open,
                on_message=self.on_message,
                on_error=self.on_error,
                on_close=self.on_close,
            )
        except Exception:
            logging.exception("BAOS Webservice down, try reconnect")

        # Set dispatcher to automatic reconnection, 5 second reconnect delay if connection closed unexpectedly
        self.ws.run_forever(ping_interval=60, ping_timeout=2, ping_payload="keep alive")

    def on_open(self, ws):
        logging.info(f"Opened connection for websocket id {id(self.ws)}")

    def on_error(self, ws, error):
        logging.error(error)

    def on_close(self, ws, close_status_code, close_msg):
        logging.info(f"Closing websocket id {id(self.ws)} with token {self.token}")
        self.ws.close()
        self.ws.keep_running = False


class MonitorWebsocket(BaseWebsocket):
    def on_message(self, ws, message):
        logging.info(f"BAOS event:\n{message}\n")
        message = json.loads(message)
        knx_monitor.DBActions.monitor_status_save_777(message)


class KNXWriteWebsocket(BaseWebsocket):
    def on_message(self, ws, message):
        ...
