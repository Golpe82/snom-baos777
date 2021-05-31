#!/usr/bin/env python3

# TOD0: send syslog messages direct to python programm, instead
# saving first into a file.
# Maybe with https://www.rsyslog.com/doc/master/configuration/modules/omprog.html ?
# example: https://www.bggofurther.com/2021/03/use-rsyslog-omprog-with-a-python-script/
'''Reads syslog file where ambient light sensor values are stored'''
import os
import subprocess
import select
import time
import requests
import re

import snom_syslog_parser as als_parser

CONF_FILE = '/etc/rsyslog.d/als_snom.conf'
SYSLOG_FILE = '/usr/local/gateway/snomsyslogknx/als_snom.log'
KNX_STATI = '/usr/local/gateway/knxmonitor/KNX_stati.csv'
CONTENTS = {
    'light sensor value': 'ALS_VALUE',
    'light sensor key': 'ALS_KEY',
}

def get_status(groupaddress):
    status = None
    with open(KNX_STATI) as knx_stati:
        while True:
            address_info = knx_stati.readline()

            if not address_info:
                break

            if groupaddress in address_info:
                status = address_info.split(",")[3]

    return status


def main():
    print(als_parser.get_phones_info(CONF_FILE))

    LIGHT_SENSOR_VALUE = CONTENTS.get('light sensor value')
    LIGHT_SENSOR_KEY = CONTENTS.get('light sensor key')
    FILE_EXISTS = os.path.isfile(CONF_FILE)
    parser = als_parser.RSyslogParser()

    if not FILE_EXISTS:
        open(CONF_FILE, 'a').close()

    FILE_SIZE = os.path.getsize(CONF_FILE)

    if not FILE_SIZE:
        ip_address = input("Log ALS values of ip: ")
        als_parser.add_ip_client(ip_address, CONF_FILE, SYSLOG_FILE)

    f = subprocess.Popen(['tail', '-F', SYSLOG_FILE],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    while True:
        #home:
        #if get_status('1/2/20') == 'on':
        #snom:
        
        if get_status('1/1/20') == 'on':
            
            if p.poll(0.1):
                last_message = f.stdout.readline()
                last_message = last_message.decode('utf-8')

                if LIGHT_SENSOR_VALUE in last_message:
                    message = parser.get_message(
                        last_message, LIGHT_SENSOR_VALUE)
                    raw_value = message.get('value')
                    value = als_parser.to_lux(raw_value)

                    if value < 100:
                        try:
                            # home
                            # requests.get('http://192.168.178.47:1234/1/2/21-plus')
                            # snom:
                            requests.get('http://10.110.16.63:1234/1/1/21-plus')
                        except:
                            print(
                                'KNX gateway not reachable or invalid groupaddress/value')

                    elif value > 110:
                        try:
                            # home:
                            # requests.get('http://192.168.178.47:1234/1/2/21-minus')
                            # snom:
                            requests.get('http://10.110.16.63:1234/1/1/21-minus')
                        except:
                            print(
                                'KNX gateway not reachable or invalid groupaddress/value')

                    print(
                        f"Ambientlight sensor value: { value } Lux\t{ raw_value } raw")

            time.sleep(0.1)


if __name__ == "__main__":
    main()
