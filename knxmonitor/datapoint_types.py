"""Handles frame payload depending on datapointtype"""
import logging

PATTERNS = {
    "DPT1": "^DPS?T-1-?",
    "DPT3": "^DPS?T-3-?",
    "DPT5": "^DPS?T-5-?",
}

def get_DPT1_formatted(raw_value):
    VALUES = {"on": 0x81, "off": 0x80}

    for key, value in VALUES.items():
        if raw_value == value:
            return key

    return "wrong value"


def get_DPT3_formatted(raw_value):
    MASK = 0x07
    VALUES = {
        "stop": range(0x81),
        "decrease": range(0x81, 0x88),
        "increase": range(0x88, 0x8F + 0x01),
    }

    step = raw_value & MASK

    for key, value in VALUES.items():
        if raw_value in value:
            return f"{ key } { step }"

    return "wrong value"


def get_DPT5_formatted(raw_value):
    VALUES = {"scale": range(0xFF)}
    logging.info(f"dpt5 value {hex(raw_value)}")

    if raw_value in VALUES.get("scale"):
        return f"{round((raw_value * 100) / 255)}%"
    
    elif raw_value == 0xFF:
        return "100%"

    return "wrong value"


class DptHandlers:
    def __init__(self, raw_value):
        self.FORMATTED_VALUES = {
            "DPT1": get_DPT1_formatted(raw_value),
            "DPT3": get_DPT3_formatted(raw_value),
            "DPT5": get_DPT5_formatted(raw_value),
        }

    def get_formatted_value(self, dpt):
        return self.FORMATTED_VALUES.get(dpt)
