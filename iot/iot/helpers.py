"""Help functions for iot project"""
import socket

def get_local_ip():
    local_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        local_socket.connect(('10.255.255.255', 1))
        local_ip = local_socket.getsockname()[0]
    except Exception:
        local_ip = '127.0.0.1'
    finally:
        local_socket.close()
    return local_ip
