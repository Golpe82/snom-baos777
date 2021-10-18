import logging
import json

from han_fun_interfaces import InterfaceTypes, OnOff
from han_fun_profiles import Profiles


FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG
HAN_FUN_PROFILES = Profiles.__subclasses__()

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


def send_data(client_handle, device_id, requested_data):
    on_off_commands = OnOff.get_on_off_commands()

    if requested_data in on_off_commands:
        iface_id = OnOff.IFACE_ID.value
        iface_member = on_off_commands.get(requested_data)
        requested_data = ""

    
    cookie = client_handle.fun_msg(
        ### Message network layer:
        src_dev_id=0x00,
        src_unit_id=0x02,  # unit id of concentrator = 0x02
        dst_dev_id=device_id,
        dst_unit_id=0x01,
        ### Message transport layer:
        # reserved for future
        ### Message application layer:
        msg_type=0x01,  # command type
        interface_type=InterfaceTypes.SERVER.value,
        interface_id=iface_id,
        interface_member=iface_member,
        data=requested_data,
    )

    return cookie


def get_devices(client_handle):
    devices_objects = client_handle.get_dev_table()
    devices = {}

    for device_item in devices_objects.devices:
        device = f"device { hex(device_item.id) }"
        devices[device] = {
            "name": "no name assigned",
            "location": "no location assigned",
            "id": device_item.id,
            "hex id": hex(device_item.id),
            "ipui": device_item.ipui
        }

        for unit_item in device_item.units:
            unit = f"unit { hex(unit_item.id) }"
            devices[device][unit] = {
                "id": unit_item.id,
                "hex id": hex(unit_item.id),
                "type": unit_item.type,
                "hex type": hex(unit_item.type),
                "profile": get_han_fun_profile(unit_item.type)
            }

            for interface_item in unit_item.interfaces:
                interface = f"interface { hex(interface_item.id) }"
                devices[device][unit][interface]={
                    "id": interface_item.id,
                    "hex id": hex(interface_item.id),
                    "type": interface_item.type,
                    "hex type": hex(interface_item.type),
                }

    return json.dumps(devices, sort_keys=True, indent=4)

def get_han_fun_profile(unit_type):
    for profile_type in HAN_FUN_PROFILES:
        try:
            profile = profile_type(unit_type)
            return profile.name
        except ValueError:
            logging.warning(f"Profile { unit_type } not in { profile_type }")
