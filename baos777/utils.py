import time
import sys
from http import HTTPStatus
import logging

import requests


def wait(seconds):
    for remaining in range(seconds, 0, -1):
        sys.stdout.write("\r")
        sys.stdout.write(f"{remaining} seconds remaining...")
        sys.stdout.flush()
        time.sleep(1)

    sys.stdout.write("\n0 seconds remaining\n")


def send_urls(urls: list) -> None:
    for url in urls:
        try:
            response = requests.get(url)

            if response.status_code != HTTPStatus.OK:
                raise response.raise_for_status()
        except Exception:
            logging.error(f"exception sending {url}:")

        logging.info(f"Sent url {url}")
