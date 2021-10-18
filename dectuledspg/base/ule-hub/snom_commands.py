import sys
import logging

import han_client
import snom_actions as snm_actn

FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)


def send_user_data(client_handle, argv):
    """
    SYNOPSIS
    General:
        send device_id data_string
    Boolean values:
        send device_id [on|off|toggle]

    DESCRIPTION
    Send a character string from the hub to the specified device. The string
    must not contain spaces. Returns a fail if the specified device is not
    registered.
    """
    all_arguments = len(argv) == 3

    if all_arguments:
        _, device_id, user_data = argv

    else:
        logging.error("send requires a device ID and data")
        return

    try:
        device_id = int(device_id)
    except ValueError:
        logging.info("The device ID (%s) must be a number", device_id)
        return

    snm_actn.send_data(client_handle, device_id, user_data)
    logging.info(
        "Device %s: message data %s has been queued for delivery ...", device_id, user_data
    )

def list_devices(client_handle, argv):
    """
    SYNOPSIS
    devices
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

def device_info(client_handle, argv):
    """
    SYNOPSIS
    device_info device_id
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
    open_duration = "120"  # default value

    if len(argv) == 2:
        if not argv[1].isdigit():
            print("The open duration (%s) has to be a number" % argv[1])
            return
        else:
            open_duration = argv[1]

    resp = client_handle.open_reg(open_duration)
    if resp.success:
        logging.info("Registration window open")
    else:
        logging.info("Error: failed to open registration window")

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
        logging.info("Registration window closed")
    else:
        logging.info("Error: failed to close registration window")

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
        local_delete = argv[2].lower() == "y"
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
        interface_id=0x7F11,  # ULE Voice Call interface
        interface_member=1,
    )
    logging.info(
        "Device {}: message has been queued for delivery ...".format(device_id)
    )


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

    DESCRIPTION            print(data)
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
        int(value, 16)  # check this is a hex number, will hit except ValueError if not
    except ValueError:
        print("Error: the value must be a hex number")
        request_valid = False

    length = han_client.EEPROM_PARAMS[param]
    if not len(value) == length * 2:
        print(
            "Error: the value is the wrong length, it has to be {} bytes".format(length)
        )
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
    prints help on API commands

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
            print("  " + command)
    else:
        try:
            cmd = commands.get(argv[1])
            print(cmd.__doc__)
        except TypeError:
            print(
                "'{}' is not a command. 'help' for a list of commands".format(argv[1])
            )

commands = {
    "open_reg": open_reg,
    "close_reg": close_reg,
    "send": send_user_data,
    "call": start_voice_call,
    "release": end_voice_call,
    "devices": list_devices,
    "device_info": device_info,
    "delete": delete_device,
    "get_black_list": get_black_list_dev_table,
    "get_sw_version": get_software_version,
    "get_hw_version": get_hardware_version,
    "get_eeprom_parameter": get_eeprom_parameter,
    "set_eeprom_parameter": set_eeprom_parameter,
    "debug_print": debug_print,
    "help": help_on_commands,
    "q": end_han_app,
}
