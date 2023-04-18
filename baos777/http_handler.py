import logging
import json
from http import HTTPStatus

import baos777.utils as baos_utils


class HTTPHandler:
    def __init__(self, baos777_websocket, response, credentials):
        self.websocket = baos777_websocket
        self.response = response
        self.credentials = credentials
        self.username = credentials.get("username")
        self.password = credentials.get("password")

    def handle(self, exception=None):
        if self.response.status_code == HTTPStatus.UNAUTHORIZED:
            raise Exception(
                f"Unauthorized. Credentials: {self.credentials}"
            ) from exception
        elif self.response.status_code == HTTPStatus.TOO_MANY_REQUESTS:
            self.retry_after_login_block()

    def retry_after_login_block(self):
        login_block = json.loads(self.response.text)
        seconds_until_login_unblocked = login_block.get("login_blocked_for_s")
        logging.error(
            f"Too many requests. Login blocked for {seconds_until_login_unblocked} seconds"
        )
        baos_utils.wait(seconds_until_login_unblocked)
        logging.info("Trying to log in again...")
        self.websocket.login(self.username, self.password)
