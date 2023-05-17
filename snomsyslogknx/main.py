import socketserver

from syslog_udp_handler import SyslogUDPHandler

HOST, PORT = "0.0.0.0", 514

if __name__ == "__main__":
    try:
        server = socketserver.UDPServer((HOST, PORT), SyslogUDPHandler)
        server.serve_forever()
    except (IOError, SystemExit):
        raise
    except KeyboardInterrupt:
        print("\nCrtl+C Pressed. Shutting down.")
