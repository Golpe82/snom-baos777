#!/usr/bin/env python3
#
# SPDX-License-Identifier: MIT
"""
HAN App
"""

from __future__ import unicode_literals
import shlex
import logging

from prompt_toolkit import prompt
from prompt_toolkit.history import InMemoryHistory
from prompt_toolkit.contrib.completers import WordCompleter

import han_client
import snom_han_handlers as snm_hndl
from snom_commands import commands, command_not_found


FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

#
# callback handlers
#


def process_rx_data(client, data_str):
    """Custom handler for the received ascii messages from the HAN server."""
    # Do something with the data received from the CMBS block.
    # This could be something received over the air or from
    # inside the CMBS block
    logging.info("HAN Client <<-- HAN Server\n" + data_str)


def handle_dev_registered(client, msg):
    device_id = int(msg.params["DEV_ID"])
    logging.info("Device {}: registered (or registration updated)".format(device_id))


def handle_reg_closed(client, msg):
    reason = msg.params["REASON"]
    logging.info("Registration window closed (reason: {})".format(reason))


def handle_fun_msg_res(client, msg):
    device_id = int(msg.params["DEV_ID"])
    logging.info("Device {}: message delivered.".format(device_id))


def handle_call_establish_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    participant = msg.params["PARTICIPANT"]
    if participant[0] == "D":
        participant = "Device {}".format(int(participant[1:]))
    else:
        participant = "Handset " + participant
    logging.info("Call {}: established with {}".format(call_id, participant))


def handle_call_dev_released_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    device_id = int(msg.params["DEV_ID"])
    logging.info("Call {}: device {} released".format(call_id, device_id))


def handle_call_release_ind(client, msg):
    call_id = int(msg.params["CALL_ID"])
    logging.info("Call {}: released".format(call_id))
    pass


def main():
    client_handle = han_client.HANClient()
    client_handle.set_debug_printing(0)
    client_handle.set_rx_message_callback(process_rx_data)
    client_handle.subscribe("dev_registered", handle_dev_registered)
    client_handle.subscribe("reg_closed", handle_reg_closed)
    client_handle.subscribe("fun_msg_res", handle_fun_msg_res)
    client_handle.subscribe("call_establish_indication", handle_call_establish_ind)
    client_handle.subscribe("dev_released_from_call", handle_call_dev_released_ind)
    client_handle.subscribe("call_release_indication", handle_call_release_ind)

    ### snom custom handlers
    client_handle.subscribe("fun_msg", snm_hndl.handle_fun_msg)

    client_handle.start()
    logging.info("HAN client started")

    history = InMemoryHistory()

    # Make the list of commands for the completer
    command_list = commands.keys()
    command_completer = WordCompleter(command_list, ignore_case=True)

    while True:
        user_command = prompt(
            "> ",
            history=history,
            patch_stdout=True,
            completer=command_completer,
            complete_while_typing=False,
        )
        argv = shlex.split(user_command)

        if not argv:
            continue

        cmd = argv[0]

        commands.get(cmd, command_not_found)(client_handle, argv)


if __name__ == "__main__":
    main()
