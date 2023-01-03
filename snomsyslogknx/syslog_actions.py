import requests
import logging


class Hosts:
    DEV_HOST = "10.110.16.101"
    LOCALHOST = "localhost"


POST_STATUS_URL = f"http://{Hosts.LOCALHOST}:8000/knx/values"
DEV_POST_STATUS_URL = f"http://{Hosts.DEV_HOST}:8000/knx/values"
# GET_RULES_URL = "http://localhost:8000/knx/rules/"
KNX_URL = f"http://{Hosts.LOCALHOST}:1234/"
DEV_GATEWAY_URL = f"http://{Hosts.DEV_HOST}:1234/"
STATUS_URL = f"http://{Hosts.LOCALHOST}:8000/knx/status/"
DEV_STATUS_URL = f"http://{Hosts.DEV_HOST}:8000/knx/status/"

logging.basicConfig(level=logging.INFO)


class DPT3Values:
    INCREASE = "-plus"
    DECREASE = "-minus"


class DBActions(object):
    def als_save(self, client_ip, client_mac, raw_value, value):
        data = {
            "mac_address": client_mac,
            "ip_address": client_ip,
            "raw_value": raw_value,
            "value": value,
        }
        try:
            requests.post(POST_STATUS_URL, data=data)
        except requests.exceptions.ConnectionError:
            logging.warning(
                f"Default localhost not reachable, trying {DEV_POST_STATUS_URL}..."
            )
            requests.post(DEV_POST_STATUS_URL, data=data)
        except Exception:
            logging.exception(f"Could not post data {data}:\n")


class KNXActions(object):
    def __init__(self, client_info):
        self.client_info = client_info
        self.client_label = client_info.get("label")

    def knx_dimm_relative(self, groupaddress, lux_value):
        client_min_brightness = self.client_info.get("min brightness")
        client_max_brightness = self.client_info.get("max brightness")

        if lux_value < client_min_brightness:
            self._knx_increase(groupaddress)
        elif lux_value > client_max_brightness:
            self._knx_decrease(groupaddress)

    def _knx_increase(self, groupaddress):
        value = DPT3Values.INCREASE
        logging.info(f"{self.client_label} dimming up {groupaddress}")

        try:
            requests.get(f"{KNX_URL}{groupaddress}{value}")
        except requests.exceptions.ConnectionError:
            logging.warning(
                f"Default localhost not reachable, trying {DEV_GATEWAY_URL}..."
            )
            requests.get(f"{DEV_GATEWAY_URL}{groupaddress}{value}")
        except Exception:
            logging.exception(
                f"Could not increase {groupaddress}."
                "KNX gateway not reachable or invalid groupaddress/value:\n"
            )

    def _knx_decrease(self, groupaddress):
        value = DPT3Values.DECREASE
        logging.info(f"{self.client_label} dimming down {groupaddress}")

        try:
            requests.get(f"{KNX_URL}{groupaddress}{value}")
        except requests.exceptions.ConnectionError:
            logging.warning(
                f"Default localhost not reachable, trying {DEV_GATEWAY_URL}..."
            )
            requests.get(f"{DEV_GATEWAY_URL}{groupaddress}{value}")
        except Exception:
            logging.exception(
                f"Could not decrease {groupaddress}."
                "KNX gateway not reachable or invalid groupaddress/value:\n"
            )

    def knx_send_celsius(self, groupaddress, celsius_value):
        logging.info(f"{self.client_label} sending {celsius_value}°C to {groupaddress}")
        path = f"{groupaddress}-send_celsius={celsius_value}"

        try:
            url = f"{KNX_URL}{path}"
            logging.debug(f"Trying to send url {url}...")
            requests.get(url)
        except requests.exceptions.ConnectionError:
            logging.warning(
                f"Default localhost not reachable, trying {DEV_GATEWAY_URL}..."
            )
            url = f"{DEV_GATEWAY_URL}{path}"
            logging.debug(f"Trying to send url {url}...")
            requests.get(url)
        except Exception:
            logging.exception(
                f"Could not send {celsius_value}°C to {groupaddress}."
                "KNX gateway not reachable or invalid groupaddress/value:\n"
            )

    def get_groupaddress_status(self, groupaddress):
        try:
            status = requests.get(f"{STATUS_URL}{groupaddress}/")

        except requests.exceptions.ConnectionError:
            logging.warning(
                f"Default localhost not reachable, trying {DEV_GATEWAY_URL}..."
            )
            status = requests.get(f"{DEV_STATUS_URL}{groupaddress}/")

        except Exception:
            logging.exception(f"No status for groupaddress {groupaddress}")

        return status.json().get("Status")
