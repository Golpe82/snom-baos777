import logging

from han_fun_interfaces import InterfaceTypes, OnOff


FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

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
