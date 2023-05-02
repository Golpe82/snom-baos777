from dataclasses import dataclass, field
from typing import Any

@dataclass
class DatapointValue:
    datapoint_format: str
    value: str
    formatted_value: Any = field(init=False)

    def __post_init__(self):
        self._set_formatted_value()

    def _set_dpt1(self):
        dpt1_values = {"on": True,"off": False}
        self.formatted_value = dpt1_values.get(self.value)

    def _set_dpt9(self):
        self.formatted_value = float(self.value)

    def _set_formatted_value(self):
        _set_method = f"_set_{self.datapoint_format.lower()}"

        if hasattr(self, _set_method):
            method = getattr(self, _set_method)
            if callable(method):
                method()