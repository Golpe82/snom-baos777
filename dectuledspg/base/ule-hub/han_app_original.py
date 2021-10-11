#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
"""
HAN App
"""

from __future__ import unicode_literals
import shlex
import sys
import datetime
from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter

import han_client


def log(str):
    print(timestamp() + " " + str)


def timestamp():
    curr_time = datetime.datetime.now()
    formatted_time = curr_time.strftime("%H:%M:%S.%f")[:-3]
    return formatted_time

#
# callback handlers
#


def process_rx_data(client, data_str):
    """Custom handler for the received ascii messages from the HAN server."""
    # Do something with the data received from the CMBS block.
    # This could be something received over the air or from
    # inside the CMBS block
    log("HAN Client <<-- HAN Server\n" + data_str)


def handle_dev_registered(client, msg):
    device_id = int(msg.params["DEV_ID"])
    log("Device {}: registered (or registration updated)".format(device_id))


def handle_reg_closed(client, msg):
    reason = msg.params["REASON"]
    log("Registration window closed (reason: {})".format(reason))


def handle_fun_msg(client, msg):
    device_id = int(msg.params["SRC_DEV_ID"])
    unit_id = int(msg.params["SRC_UNIT_ID"])
    interface_id = int(msg.params["INTRF_ID"])

    if unit_id == 0 and interface_id == 0x0115:
        # device management unit, keep-alive interface
        log("Device {}: keep alive".format(device_id))

    if unit_id == 1:
        # voice call unit
        log("Device {}: message from voice call unit".format(device_id))

    if unit_id == 2:
        # smoke unit
        log("Device {}: message from smoke unit".format(device_id))

    if unit_id == 3:
        # ULEasy unit (raw data)
        data = msg.data.decode("utf-8")
        log("Device {}: message from raw data unit: '{}'".format(device_id, data))


def handle_fun_msg_res(client, msg):
    device_id = int(msg.params["DEV_ID"])
    log("Device {}: message delivered.".format(device_id))


def handle_call_establish_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    participant = msg.params["PARTICIPANT"]
    if participant[0] == "D":
        participant = "Device {}".format(int(participant[1:]))
    else:
        participant = "Handset " + participant
    log("Call {}: established with {}".format(call_id, participant))


def handle_call_dev_released_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    device_id = int(msg.params["DEV_ID"])
    log("Call {}: device {} released".format(call_id, device_id))


def handle_call_release_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    log("Call {}: released".format(call_id))
    pass


#
# helpers
#


def send_data(client_handle, device_id, data):
    """Sends RAW <data> to <device_id>

    All ULE expansion boards are configured to have a Unit 3 which will accept
    any message payload. Send anything you want.
    """
    # send raw data to Unit 3 (ULEasy)
    cookie = client_handle.fun_msg(
        src_dev_id=0,
        src_unit_id=0,
        dst_dev_id=device_id,
        dst_unit_id=3,  # ULEasy unit
        interface_type=0,  # server
        interface_id=0x7f16,  # ULeasy interface
        interface_member=1,
        data=data,
    )
    return cookie

#
# commands
#


def list_devices(client_handle, argv):
    """
NAME
devices - get information about all the devices

SYNOPSIS
devices

DESCRIPTION
Lists the all the information for each device registered to the hub.
    """
    index = 0
    count = 5
    while True:
        resp = client_handle.get_dev_table(index=index, count=count)
        for dev in resp.devices:
            print(dev)

        # If there are fewer devices than we have asked for we have retrieved them all,
        # otherwise we need to move the index and check if there are more.
        if len(resp.devices) < count:
            break
        else:
            index += count


def get_black_list_dev_table(client_handle, argv):
    """
NAME
get_black_list - list devices that are marked for deletion

SYNOPSIS
get_black_list

DESCRIPTION
Lists all the registered devices that are marked for deletion. If none,
reports number as zero.
    """

    index = 0
    count = 5
    devices = []

    while True:
        resp = client_handle.get_black_list_dev_table(index=index, count=count)
        devices += resp.devices

        # If there are fewer devices than we have asked for we have retrieved them all,
        # otherwise we need to move the index and check if there are more.
        if len(resp.devices) < count:
            break
        else:
            index += count

    num_blacklisted = len(devices)
    if num_blacklisted == 0:
        print("{} devices are black listed.".format(num_blacklisted))
    else:
        print("{} devices are black listed:".format(num_blacklisted))
        for dev in devices:
            print(dev)


def device_info(client_handle, argv):
    """
NAME
device_info - get information about a specified device

SYNOPSIS
device_info device_id

DESCRIPTION
List all the information for the device specified by device_id. Will return
a device ID error if the specified device is not registered.
    """

    if len(argv) < 2:
        print("device_info requires a device ID")
        return

    device_id = argv[1]
    try:
        int(device_id)
    except ValueError:
        print("The device ID has to be a number")
        return

    client_handle.get_dev_info(device_id)


def delete_device(client_handle, argv):
    """
NAME
delete - delete the registration of a device

SYNOPSIS
delete device_id [y]

DESCRIPTION
Deletes the registration for the specified device. Defaults to blacklist
deletion if the y parameter is not included. Returns a fail if the
specified device is not registered.

OPTIONS
delete device_id - blacklists the device for future deletion
delete device_id Y - locally deletes the device
delete device_id y - locally deletes the device
delete device_id * - where * is not y or Y, blacklists the device for future deletion
    """

    # Will default to blacklist deletion if there is no delete option in the
    # command or if the delete option is not y or Y

    if len(argv) < 2:
        print("delete requires a device ID")
        return

    device_id = argv[1]
    try:
        int(device_id)
    except ValueError:
        print("The device ID has to be a number")
        return

    if len(argv) == 3:
        local_delete = (argv[2].lower() == "y")
    else:
        local_delete = False

    client_handle.delete_dev(device_id, local=local_delete)


def start_voice_call(client_handle, argv):
    """
NAME
call - start a voice call with a device

SYNOPSIS
call device_id

DESCRIPTION
Starts a voice call with the specified device. Returns a fail if the specified
device is not registered.
    """
    if len(argv) < 2:
        print("This command requires a device ID")
        return

    device_id = argv[1]
    try:
        int(device_id)
    except ValueError:
        print("The device ID has to be a number")
        return

    client_handle.fun_msg(
        src_dev_id=0,
        src_unit_id=2,
        dst_dev_id=device_id,
        dst_unit_id=1,  # ULE Voice Call unit
        interface_type=1,  # server
        interface_id=0x7f11,  # ULE Voice Call interface
        interface_member=1,
    )
    log("Device {}: message has been queued for delivery ...".format(device_id))


def end_voice_call(client_handle, argv):
    """
NAME
release - end a specified voice call

SYNOPSIS
release call_id

DESCRIPTION
End a voice call with the specified call identity.
    """
    try:
        if (argv[1]).isdigit():
            client_handle.call_release(argv[1])
        else:
            print("The call ID (%s) has to be a number" % argv[1])
    except IndexError:
        print("release requires a call ID value")


def send_user_data(client_handle, argv):
    """
NAME
send - send a string to a device

SYNOPSIS
send device_id data_string

DESCRIPTION
Send a character string from the hub to the specified device. The string
must not contain spaces. Returns a fail if the specified device is not
registered.
    """

    if len(argv) == 3:
        _, device_id, user_data = argv
    else:
        print("send requires a device ID and data")
        return

    try:
        device_id = int(device_id)
    except ValueError:
        print("The device ID ({}) has to be a number".format(device_id))
        return

    send_data(client_handle, device_id, user_data)
    log("Device {}: message has been queued for delivery ...".format(device_id))


def debug_print(client_handle, argv):
    """
NAME
debug_print - switches extra print output from the HAN client on or off

SYNOPSIS
debug_print on|off

DESCRIPTION
Switches on or off print messages from within the HAN client that may be useful
when debugging programs using the API.

OPTIONS
debug_print on - switches debug printing on
debug_print off - switches debug printing off

    """
    if len(argv) != 2:
        print("debug_print needs a on/off parameter.")
        return

    if argv[1] == "on":
        client_handle.set_debug_printing(1)
    else:
        client_handle.set_debug_printing(0)


def open_reg(client_handle, argv):
    """
NAME
open_reg - open the hub for registration

SYNOPSIS
open_reg [open_duration]

DESCRIPTION
Open the hub to allow a device to register. The hub remains open
for 120 seconds or the time specified in the open_duration parameter.

OPTIONS
open_reg - opens the base for 120 seconds
open_reg * - opens the base for * seconds
    """
    open_duration = "120"   # default value

    if len(argv) == 2:
        if not argv[1].isdigit():
            print("The open duration (%s) has to be a number" % argv[1])
            return
        else:
            open_duration = argv[1]

    resp = client_handle.open_reg(open_duration)
    if resp.success:
        log("Registration window open")
    else:
        log("Error: failed to open registration window")


def close_reg(client_handle, argv):
    """
NAME
close_reg - close the hub to prohibit registration

SYNOPSIS
close_reg

DESCRIPTION
Forces the hub to close to prohibit registration.
    """
    resp = client_handle.close_reg()
    if resp.success:
        log("Registration window closed")
    else:
        log("Error: failed to close registration window")


def get_software_version(client_handle, argv):
    """
NAME
get_sw_version - get the hub software version

SYNOPSIS
get_sw_version

DESCRIPTION
Get the hub software version
    """
    client_handle.get_sw_version()


def get_hardware_version(client_handle, argv):
    """
NAME
get_hw_version - get the hub hardware version

SYNOPSIS
get_hw_version

DESCRIPTION
Get the hub hardware version
    """
    client_handle.get_hw_version()


def list_eeprom_parameters(list_all):
    for param in han_client.EEPROM_PARAMS:
        length = han_client.EEPROM_PARAMS[param]
        if (length > 0) or list_all:
            print(param)


def get_eeprom_parameter(client_handle, argv):
    """
NAME
get_eeprom_parameter - gets the value of an EEPROM parameter or all parameters

SYNOPSIS
get_eeprom_parameter <parameter | 'list' | 'all'>

DESCRIPTION
Shows the value of the specified EEPROM  parameter or lists the names of all the
EEPROM parameter or shows the value of all the EEPROM paramters.

OPTIONS
get_eeprom_parameter EEPROM_paramter_name - returns the value of the specified parameter
get_eeprom_parameter list - lists the names of all the EEPROM paramters
get_eeprom_parameter all - lists the name and value of all the EEPROM parameters
    """
    if len(argv) != 2:
        print("get_eeprom_parameter needs a parameter.")
        return

    if argv[1] == "list":
        list_eeprom_parameters(True)
    elif argv[1] == "all":
        for name in han_client.EEPROM_PARAMS:
            client_handle.get_eeprom_parameter(name)
    else:
        param = argv[1].upper()  # EEPROM parameter names are upper case
        if param in han_client.EEPROM_PARAMS:
            client_handle.get_eeprom_parameter(param)
        else:
            print("Error: unknown EEPROM parameter: '{}'".format(param))


def set_eeprom_parameter(client_handle, argv):
    """
NAME
set_eeprom_parameter - sets the value of an EEPROM parameter

SYNOPSIS
set_eeprom_parameter <parameter hex_value | 'list'>

DESCRIPTION
Set the value of the specified EEPROM paramter. Returns an error if the parameter
does not exist or is not writable, or if the hex_value length does not match the
required length (for example if a parameter requires a 16 bit value entering ABC
will cause and error where 0ABC will be accepted). Or list all the writable
EEPROM parameters.

OPTIONS
set_eeprom_parameter parameter hex_value - sets the parameter to hex_value
set_eeprom_parameter list - lists all the writable EEPROM parameters
    """
    if len(argv) < 2:
        print("set_eeprom_parameter needs more parameters.")
        return

    if argv[1] == "list":
        # Only going to list eeprom paramters that are writable
        list_eeprom_parameters(False)
        return
    else:
        param = argv[1].upper()  # EEPROM parameter names are upper case

    if eeprom_parameter_is_writable(param):
        if len(argv) != 3:
            print("set_eeprom_parameter needs two parameters.")
            return
    else:
        # No point in checking anything else if we can't write to this parameter
        return

    value = argv[2]

    if eeprom_request_valid(param, value):
        resp = client_handle.set_eeprom_parameter(param, value)
        if resp.params["STATUS"] == "SUCCEED":
            print("EEPROM parameter '{}' updated.".format(param))
        else:
            print("Error: failed updating EEPROM parameter '{}'".format(param))


def eeprom_parameter_is_writable(eeprom_parameter):
    """
    Check the eeprom parameter exists and that it is writeable
    """

    is_writable = True

    if eeprom_parameter not in han_client.EEPROM_PARAMS:
        print("Error: unknown EEPROM parameter: '{}'".format(eeprom_parameter))
        is_writable = False
    else:
        length = han_client.EEPROM_PARAMS[eeprom_parameter]
        if length == 0:
            print("Error: read-only EEPROM parameter: '{}'".format(eeprom_parameter))
            is_writable = False

    return is_writable


def eeprom_request_valid(param, value):
    """
    Check that the user supplied values are acceptable.
    """

    request_valid = True

    try:
        int(value, 16)    # check this is a hex number, will hit except ValueError if not
    except ValueError:
        print("Error: the value must be a hex number")
        request_valid = False

    length = han_client.EEPROM_PARAMS[param]
    if not len(value) == length * 2:
        print("Error: the value is the wrong length, it has to be {} bytes".format(length))
        request_valid = False

    return request_valid


def end_han_app(client_handle, argv):
    """
NAME
q - exit the han_app program

SYNOPSIS
q

DESCRIPTION
Exit the han_app program.
    """
    print("Quitting HAN Client...")
    client_handle.destroy()
    sys.exit(0)


def command_not_found(client_handle, argv):
    print("'{}' is not a command. 'help' for a list of commands".format(argv[0]))


def help_on_commands(client_handle, argv):
    """
NAME
help - prints help on API commands

SYNOPSIS
help [command]

DESCRIPTION
Prints a list of all the available commands or help on a specified command.

OPTIONS
help - prints a list of all the commands
help command - prints help on the specified command
    """
    if len(argv) < 2:
        print("The following commands are available, 'help cmd' for more information")
        command_list = commands.keys()
        for command in command_list:
            print('  ' + command)
    else:
        try:
            cmd = commands.get(argv[1])
            print(cmd.__doc__)
        except TypeError:
            print("'{}' is not a command. 'help' for a list of commands".format(argv[1]))


commands = {
    'open_reg': open_reg,
    'close_reg': close_reg,
    'send': send_user_data,
    'call': start_voice_call,
    'release': end_voice_call,
    'devices': list_devices,
    'device_info': device_info,
    'delete': delete_device,
    'get_black_list': get_black_list_dev_table,
    'get_sw_version': get_software_version,
    'get_hw_version': get_hardware_version,
    'get_eeprom_parameter': get_eeprom_parameter,
    'set_eeprom_parameter': set_eeprom_parameter,
    'debug_print': debug_print,
    'help': help_on_commands,
    'q': end_han_app,
}


def main():
    client_handle = han_client.HANClient()
    client_handle.set_debug_printing(0)
    client_handle.set_rx_message_callback(process_rx_data)
    client_handle.subscribe("dev_registered", handle_dev_registered)
    client_handle.subscribe("reg_closed", handle_reg_closed)
    client_handle.subscribe("fun_msg", handle_fun_msg)
    client_handle.subscribe("fun_msg_res", handle_fun_msg_res)
    client_handle.subscribe("call_establish_indication", handle_call_establish_ind)
    client_handle.subscribe("dev_released_from_call", handle_call_dev_released_ind)
    client_handle.subscribe("call_release_indication", handle_call_release_ind)

    client_handle.start()
    log("HAN client started")

    history = InMemoryHistory()

    # Make the list of commands for the completer
    command_list = commands.keys()
    command_completer = WordCompleter(command_list, ignore_case=True)

    while True:
        user_command = prompt("> ",
                              history=history,
                              patch_stdout=True,
                              completer=command_completer,
                              complete_while_typing=False)
        argv = shlex.split(user_command)

        if not argv:
            continue

        cmd = argv[0]

        commands.get(cmd, command_not_found)(client_handle, argv)


if __name__ == "__main__":
    main()
