import logging
from dataclasses import dataclass, field
from typing import Any

from baos777.constants import DPT1_VALUES


@dataclass
class DatapointValue:
    datapoint_format: str
    value: str
    formatted_value: Any = field(init=False)

    def __post_init__(self):
        self._set_formatted_value()

    def _set_formatted_value(self):
        _set_method = f"_set_{self.datapoint_format.lower()}"

        if hasattr(self, _set_method):
            _datapoint_value_setter = getattr(self, _set_method)
            if callable(_datapoint_value_setter):
                _datapoint_value_setter()

    def _set_dpt1(self):
        self.formatted_value = DPT1_VALUES.get(self.value)

    def _set_dpt2(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt3(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt4(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt5(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt6(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt7(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt8(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt9(self):
        self.formatted_value = float(self.value)

    def _set_dpt10(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt11(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt12(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt13(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt14(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt16(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt18(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt20(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt232(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None
