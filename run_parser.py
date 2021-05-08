#!/usr/bin/env python3
'''Reads syslog file where ambient light sensor values are stored'''
import os
import subprocess
import select
import time
import getmac

import snom_syslog_parser as als_parser

CONF_FILE = '/etc/rsyslog.d/als_snom.conf'
SYSLOG_FILE = '/usr/local/gateway/als_snom.log'


def add_syslog_ip(ip_address):
    MAC = str(getmac.get_mac_address(ip=ip_address)).replace(":", '')
    TEMPLATE = (
        f'$template snom{MAC}, "{ SYSLOG_FILE }"\n'
        f':fromhost-ip, isequal, "{ ip_address }" -?snom{MAC}\n'
        f'& stop'
    )

    with open(CONF_FILE, 'a+') as als_log:
        content = als_log.readlines()

        if TEMPLATE not in content:
            als_log.write(TEMPLATE)

        subprocess.call(["systemctl", "restart", "rsyslog"])


def main():
    parser = als_parser.RSyslogParser()
    FILE_EXISTS = os.path.isfile(CONF_FILE)

    if not FILE_EXISTS:
        open(CONF_FILE, 'a').close()

    FILE_SIZE = os.path.getsize(CONF_FILE)

    if not FILE_SIZE:
        add_syslog_ip(input("Log ALS values of ip: "))

    f = subprocess.Popen(['tail', '-F', SYSLOG_FILE],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        if p.poll(0.1):
            syslog_lines = f.stdout.readline()
            syslog_lines = syslog_lines.decode('utf-8')
            # print(syslog_lines)
            list = parser.analyse_syslog_lines([syslog_lines])

            # if list:
            #    print(list)
        time.sleep(0.1)


if __name__ == "__main__":
    main()
