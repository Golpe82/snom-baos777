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
import snom_handlers as snm_hndl
import snom_commands as snm_cmd


FORMAT = "%(asctime)s:%(levelname)s:%(message)s"
LOG_LEVEL = logging.DEBUG

logging.basicConfig(format=FORMAT, level=LOG_LEVEL)

def main():
    client_handle = han_client.HANClient()
    client_handle.set_debug_printing(0)
    client_handle.set_rx_message_callback(snm_hndl.process_rx_data)
    client_handle.subscribe("dev_registered", snm_hndl.handle_dev_registered)
    client_handle.subscribe("reg_closed", snm_hndl.handle_reg_closed)
    client_handle.subscribe("fun_msg_res", snm_hndl.handle_fun_msg_res)
    client_handle.subscribe("call_establish_indication", snm_hndl.handle_call_establish_ind)
    client_handle.subscribe("dev_released_from_call", snm_hndl.handle_call_dev_released_ind)
    client_handle.subscribe("call_release_indication", snm_hndl.handle_call_release_ind)
    client_handle.subscribe("fun_msg", snm_hndl.handle_fun_msg)

    client_handle.start()
    logging.info("HAN client started")

    history = InMemoryHistory()

    # Make the list of commands for the completer
    command_list = snm_cmd.commands.keys()
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

        snm_cmd.commands.get(cmd, snm_cmd.command_not_found)(client_handle, argv)


if __name__ == "__main__":
    main()
