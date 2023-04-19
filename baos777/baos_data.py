import requests
import logging
import json
from http import HTTPStatus

SERVER_URL = "http://10.110.16.63/"
WEBSOCKET_PATH = "websocket/"
REST_API_PATH = "rest/"
DATAPOINTS_PATH = f"{REST_API_PATH}datapoints/"
GROUPADDRESSES_PATH = f"{DATAPOINTS_PATH}addresses/"


class BAOS777Data:
    def __init__(self, token, baos_message=None):
        self.token = token
        self.auth_header = {"Authorization": f"Token token={self.token}"}
        self.datapoints = self._get_datapoints()
        self.datapoints_ids = self._get_datapoints_ids()
        self.datapoints_urls = self._get_datapoints_urls()
        self.datapoint_information = {}
        self._set_datapoint_information()
        self.baos_message = baos_message

    def _get_datapoints(self):
        try:
            logging.info("Trying to get BAOS777 datapoints")
            response = requests.get(f"{SERVER_URL}{DATAPOINTS_PATH}", headers=self.auth_header)
            
            if response.status_code != HTTPStatus.OK:
                response.raise_for_status()
        except Exception:
            logging.error(("unable to get datapoints"))
        
        response_text = json.loads(response.text)
        logging.info(response_text)
        
        return response_text.get("datapoints")

    def _get_datapoints_ids(self):
        return [datapoint_id.get("id") for datapoint_id in self.datapoints]
    
    def _get_datapoints_urls(self):
        return [datapoint.get("url") for datapoint in self.datapoints]
    
    def _set_datapoint_information(self):
        self._set_datapoint_types_by_id()
        self._set_datapoint_groupaddresses()
        logging.info(self.datapoint_information)

    def _set_datapoint_types_by_id(self):
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
                self.datapoint_information[datapoint_id] = {
                    "datapoint format": datapoint_format,
                    "datapoint type": self._get_datapoint_type(response_text)
                }

    def _get_datapoint_type(self, datapoint_response):
        datapoint_description = datapoint_response.get("description")

        return datapoint_description.get("datapoint_type")

    def _set_datapoint_groupaddresses(self):
        try:
            response = requests.get(f"{SERVER_URL}{GROUPADDRESSES_PATH}", headers=self.auth_header)
            if response.status_code != HTTPStatus.OK:
                response.raise_for_status()
        # handle 403 (no auth header given in request)
        except Exception:
            logging.error("unable to set datapoint groupaddresses")

        else:
            response_text = json.loads(response.text)
            datapoints_addresses = response_text.get("datapoints_addresses")
            self._update_datapoint_information(datapoints_addresses)

    def _update_datapoint_information(self, datapoints_addresses):
        for datapoint_address in datapoints_addresses:
            datapoint_id = datapoint_address.get("id")
            datapoint_groupaddresses = datapoint_address.get("addresses")
            datapoint = self.datapoint_information.get(datapoint_id)
            datapoint.update({"groupaddresses": datapoint_groupaddresses})
        
    def get_groupaddresses(self):
        ...

    def print_message(self):
        print(f"Incoming BAOS message:\n{self.baos_message}")

    def get_value(self):
        ...