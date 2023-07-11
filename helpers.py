"""Help functions for iot project"""
import socket
import os
import shutil
import logging

def get_local_ip():
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        local_socket.connect(("10.255.255.255", 1))
        local_ip = local_socket.getsockname()[0]
    except Exception:
        local_ip = "127.0.0.1"
    finally:
        local_socket.close()
    return local_ip


def remove_file_if_exists(file):
    if os.path.exists(file):
        os.remove(file)
        logging.warning(f"Existing file {file} deleted")


def update_directory(directory):
    if os.path.exists(directory):
        shutil.rmtree(directory)
        logging.warning(f"Existing directory {directory} removed recursively")

    os.makedirs(directory)
    logging.warning(f"Directory {directory} created")
