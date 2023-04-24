"""Module for storing and handling information of BAOS 777 indications messages"""

from dataclasses import dataclass


@dataclass
class BAOSIndicationsMessage:
    message: dict

    @property
    def indications(self):
        return self.message.get("indications")

    @property
    def values(self):
        return self.indications.get("values")

    @property
    def values_by_datapoint_id(self):
        return {
            datapoint.get("id"): datapoint.get("value") for datapoint in self.values
        }
