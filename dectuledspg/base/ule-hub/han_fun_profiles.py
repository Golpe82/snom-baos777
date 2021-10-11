"""All Profiles Defined in Han-Fun protocol"""

import logging
import json
from enum import Enum, IntEnum


DEBUG = True
FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


class HomeControlProfiles(IntEnum):
    ON_OFF_SWITCHABLE = 0x0100
    ON_OFF_SWITCH = 0x0101
    LEVEL_CONTROLLABLE = 0x0102
    LEVEL_CONTROL = 0x0103
    LEVEL_CONTROLLABLE_SWITCHABLE = 0x0104
    LEVEL_CONTROL_SWITCH = 0x0105
    AC_OUTLET = 0x0106
    AC_OUTLET_WITH_POWER_METERING = 0x0107
    SIMPLE_LIGHT = 0x0108
    DIMMABLE_LIGHT = 0x0109
    DIMMER_SWITCH = 0x010A
    DOOR_LOCK = 0x010B
    DOOR_BELL = 0x010C
    POWER_METER = 0x010D
    TEMPERATURE_SENSOR = 0x010E
    HUMIDITY_SENSOR = 0x010F
    AIR_PRESSURE_SENSOR = 0x0110
    BUTTON = 0x0111
    CONTROLLABLE_THERMOSTAT = 0x0112
    LED = 0x0113
    ENVIROMENT_MONITOR = 0x0114
    COLOUR_BULB = 0x0115
    DIMMABLE_COLOUR_BULB = 0x0116
    TRACKER = 0x0117
    SIMPLE_KEYPAD = 0x0118


class SecurityProfiles(IntEnum):
    DETECTOR = 0x0200
    DOOR_OPEN_CLOSE_DETECTOR = 0x0201
    WINDOW_OPEN_CLOSE_DETECTOR = 0x0202
    MOTION_DETECTOR = 0x0203
    SMOKE_DETECTOR = 0x0204
    GAS_DETECTOR = 0x0205
    FLOOD_DETECTOR = 0x0206
    GLASS_BREAK_DETECTOR = 0x0207
    VIBRATION_DETECTOR = 0x0208
    LIGHT_SENSOR = 0x0209
    SIREN = 0x0280
    ALERTABLE = 0x0281


class HomecareProfiles(IntEnum):
    PENDANT = 0x0300


class ApplicationProfiles(IntEnum):
    UI_LOCK = 0x0401
    USER_INTERFACE = 0x0410
    GENERIC_APPLICATION_LOGIC = 0x0411


class ProprietaryProfiles(Enum):
    PROPRIETARY = range(0xFF00, 0xFFFF)


profiles = {
    "Homecontrol": {
        str(profile): hex(profile.value) for profile in HomeControlProfiles
    },
    "Security": {str(profile): hex(profile.value) for profile in SecurityProfiles},
    "Homecare": {str(profile): hex(profile.value) for profile in HomecareProfiles},
    "Application": {
        str(profile): hex(profile.value) for profile in ApplicationProfiles
    },
    "Proprietary": {
        str(profile): str(profile.value) for profile in ProprietaryProfiles
    },
}


def get_profile_groups(to_json=False):
    if to_json:
        return json.dumps(profiles, sort_keys=True, indent=4)

    return profiles


def get_profile_group(group, to_json=False):
    if group in profiles.keys():
        if to_json:
            profile_group = profiles.get(group, None)

            return json.dumps(profile_group, sort_keys=True, indent=4)

        return profiles.get(group, None)

    return (
        "\nWrong Han-Fun profile group.\n"
        "Available groups:\n"
        f"{ list(profiles.keys()) }"
    )


def get_profile_id(profile_name, to_json=False):
    available_profiles = get_profile_groups()
    profiles = {}

    for profile_group in available_profiles.values():
        for profile, uid in profile_group.items():
            if profile.find(profile_name) > 0:
                profiles[profile] = uid

    if profiles:
        if to_json:
            return json.dumps(profiles, sort_keys=True, indent=4)

        return profiles

    return (
        "\nNo such a profile.\n"
        "Available profiles:\n"
        f"{ json.dumps(available_profiles, sort_keys=True, indent=4) }"
    )


if __name__ == "__main__":
    if DEBUG:
        profile_group_to_print = "Homecontrol"
        logging.info(
            "\n---> You are seeing this because DEBUG is set to 'True'.\n"
            "---> Set DEBUG to 'False' to omit this output:\n"
        )
        logging.info(get_profile_groups(to_json=True))
        logging.info(get_profile_group("Homecontrol", to_json=True))
        logging.info(get_profile_id("AC_OUTLET", to_json=True))
