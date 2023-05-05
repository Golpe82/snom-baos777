import requests
import logging
import json
from http import HTTPStatus


from baos777.baos_websocket import BAOS777_IP
from baos777.constants import BAOS777Commands as cmd
from baos777.datapoint_values import DatapointValue

SERVER_URL = f"http://{BAOS777_IP}/"
WEBSOCKET_PATH = "websocket/"
REST_API_PATH = "rest/"
DATAPOINTS_PATH = f"{REST_API_PATH}datapoints/"
GROUPADDRESSES_PATH = f"{DATAPOINTS_PATH}addresses/"

SENDING_GROUPADDRESS = 0


class BAOS777Interface:
    def __init__(self, token, baos_message=None):
        self.token = token
        self.auth_header = {"Authorization": f"Token token={self.token}"}
        self.datapoints = self._get_datapoints()
        self.datapoints_ids = self._get_datapoints_ids()
        self.datapoints_urls = self._get_datapoints_urls()
        self.datapoints_information = {}
        self._set_datapoints_information()
        self.baos_message = baos_message

    def _get_datapoints(self):
        try:
            response = requests.get(
                f"{SERVER_URL}{DATAPOINTS_PATH}", headers=self.auth_header
            )

            if response.status_code != HTTPStatus.OK:
                response.raise_for_status()
        except Exception:
            logging.error(("unable to get datapoints"))

        response_text = json.loads(response.text)

        return response_text.get("datapoints")

    def _get_datapoints_ids(self):
        return [datapoint_id.get("id") for datapoint_id in self.datapoints]

    def _get_datapoints_urls(self):
        return [datapoint.get("url") for datapoint in self.datapoints]

    def _set_datapoints_information(self):
        self._set_datapoints_type_by_id()
        self._set_datapoints_groupaddresses()

    def _set_datapoints_type_by_id(self):
        for datapoint_url in self.datapoints_urls:
            try:
                response = requests.get(datapoint_url, headers=self.auth_header)
                if response.status_code != HTTPStatus.OK:
                    response.raise_for_status()
            # handle 403 (no auth header given in request)
            except Exception:
                logging.error("unable to set datapoint types")

            else:
                response_text = json.loads(response.text)
                datapoint_id = response_text.get("id")
                datapoint_format = response_text.get("Format")
                self.datapoints_information[datapoint_id] = {
                    "datapoint format": datapoint_format,
                    "datapoint type": self._get_datapoint_type(response_text),
                }

    def _get_datapoint_type(self, datapoint_response):
        datapoint_description = datapoint_response.get("description")

        return datapoint_description.get("datapoint_type")

    def _set_datapoints_groupaddresses(self):
        try:
            response = requests.get(
                f"{SERVER_URL}{GROUPADDRESSES_PATH}", headers=self.auth_header
            )
            if response.status_code != HTTPStatus.OK:
                response.raise_for_status()
        # handle 403 (no auth header given in request)
        except Exception:
            logging.error("unable to set datapoint groupaddresses")

        else:
            response_text = json.loads(response.text)
            datapoints_addresses = response_text.get("datapoints_addresses")
            self._update_datapoints_information(datapoints_addresses)

    def _update_datapoints_information(self, datapoints_addresses):
        for datapoint_address in datapoints_addresses:
            datapoint_id = datapoint_address.get("id")
            datapoint_groupaddresses = datapoint_address.get("addresses")
            datapoint = self.datapoints_information.get(datapoint_id)
            datapoint.update({"groupaddresses": datapoint_groupaddresses})

    @property
    def sending_groupaddresses(self):
        return {
            datapoint_id: information.get("groupaddresses")[SENDING_GROUPADDRESS]
            for datapoint_id, information in self.datapoints_information.items()
            if information.get("groupaddresses")
        }

    def get_sending_groupaddress(self, datapoint_id):
        return self.sending_groupaddresses.get(datapoint_id)

    def _get_datapoint_id_by_groupaddress(self, groupaddress):
        return next(
            (
                datapoint_id
                for datapoint_id, sending_groupaddress in self.sending_groupaddresses.items()
                if groupaddress == sending_groupaddress
            ),
            None,
        )

    def _get_datapoint_information_by_groupaddress(self, groupaddress):
        groupaddress_datapoint_id = self._get_datapoint_id_by_groupaddress(groupaddress)

        return next(
            (
                information
                for datapoint_id, information in self.datapoints_information.items()
                if datapoint_id == groupaddress_datapoint_id
            ),
            None,
        )

    def read_value(self, groupaddress):
        datapoint_id = self._get_datapoint_id_by_groupaddress(groupaddress)
        url = f"{SERVER_URL}{DATAPOINTS_PATH}{datapoint_id}"
        response_raw = requests.get(url, headers=self.auth_header)
        response = json.loads(response_raw.text)
        raw_value = response.get("value")

        logging.info(f"Got raw value {raw_value}")
        datapoint_information = self._get_datapoint_information_by_groupaddress(
            groupaddress
        )
        logging.info(f"Groupaddress datapoint information:\n{datapoint_information}")
        datapoint_format = datapoint_information.get("datapoint format")
        value = self._format_value(raw_value, datapoint_format)

        return value

    def _format_value(self, raw_value, datapoint_format):
        formatted_value = ""

        if datapoint_format == "DPT1":
            if raw_value == True:
                formatted_value = "on"
            elif raw_value == False:
                formatted_value = "off"
            else:
                formatted_value = f"unknown raw value {raw_value}"
        elif datapoint_format == "DPT5":
            formatted_value = f"{round(raw_value*100/255)}%"
        else:
            formatted_value = f"unknown datapoint format {datapoint_format}"

        return formatted_value

    def send_value(self, groupaddress, value):
        datapoint_id = self._get_datapoint_id_by_groupaddress(groupaddress)
        datapoint_information = self.datapoints_information.get(datapoint_id)
        datapoint_format = datapoint_information.get("datapoint format")
        url = f"{SERVER_URL}{DATAPOINTS_PATH}{datapoint_id}"
        payload = {
            "command": cmd.SET_VALUE_AND_SEND_ON_BUS,
            "value": self._get_datapoint_raw_value(datapoint_format, value),
        }
        requests.put(url, json.dumps(payload), headers=self.auth_header)

    def _get_datapoint_raw_value(self, datapoint_format, value):
        datapoint_value = DatapointValue(datapoint_format, value)

        return datapoint_value.formatted_value
