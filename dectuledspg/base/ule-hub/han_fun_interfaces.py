"""All interfaces defined in Han-Fun protocol"""

import logging
import json
from enum import Enum, IntEnum


DEBUG = True
FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


class FunctionalInterfaces(IntEnum):
    ALERT = 0x0100
    ON_OFF = 0x0200
    LEVEL_CONTROL = 0x0201
    COLOUR_CONTROL = 0x0202
    KEYPAD = 0x0203
    POWER_METERING = 0x0300
    TEMPERATURE = 0x0301
    HUMIDITY = 0x0302
    THERMOSTAT = 0x0303
    BUTTON = 0x0304
    VISUAL_CONTROL = 0x0305
    AIR_PRESSURE = 0x0306
    LIGHT_SENSOR = 0x0307


class ReserverdInterfaces(Enum):
    PROPRIETARY_RESERVED = range(0x7F00, 0x7FFE)
    UID_RESERVED = 0x7FFF


interfaces = {
    "Functional": {
        str(interface): hex(interface.value) for interface in FunctionalInterfaces
    },
    "Reserved": {
        str(interface): str(interface.value) for interface in ReserverdInterfaces
    },
}


def get_interface_groups(to_json=False):
    if to_json:
        return json.dumps(interfaces, sort_keys=True, indent=4)

    return interfaces


def get_interface_group(group, to_json=False):
    if group in interfaces.keys():
        if to_json:
            interface_group = interfaces.get(group, None)

            return json.dumps(interface_group, sort_keys=True, indent=4)

        return interfaces.get(group, None)

    return (
        "\nWrong Han-Fun interface group.\n"
        "Available groups:\n"
        f"{ list(interfaces.keys()) }"
    )


def get_interface_id(interface_name, to_json=False):
    available_interfaces = get_interface_groups()
    requested_interfaces = {}

    for interface_group in available_interfaces.values():
        for interface, uid in interface_group.items():
            if interface.find(interface_name) > 0:
                requested_interfaces[interface] = uid

    if requested_interfaces:
        if to_json:
            return json.dumps(requested_interfaces, sort_keys=True, indent=4)

        return requested_interfaces

    return (
        "\nNo such a interface.\n"
        "Available interfaces:\n"
        f"{ json.dumps(available_interfaces, sort_keys=True, indent=4) }"
    )


if __name__ == "__main__":
    if DEBUG:
        INTERFACE_GROUP_TO_PRINT = "Functional"
        INTERFACE_TO_PRINT = "COLOUR_CONTROL"
        logging.info(
            "\n---> You are seeing this because DEBUG is set to 'True'.\n"
            "---> Set DEBUG to 'False' to omit this output:\n"
        )
        logging.info(get_interface_groups(to_json=True))
        logging.info(get_interface_group(INTERFACE_GROUP_TO_PRINT, to_json=True))
        logging.info(get_interface_id(INTERFACE_TO_PRINT, to_json=True))
