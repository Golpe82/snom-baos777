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
import datetime

import snom_syslog_parser as als_parser
import knx_monitor
from iot import helpers

CONTENTS = {
    'light sensor value': 'ALS_VALUE',
    'light sensor key': 'ALS_KEY',
}


def main():
    GATEWAY_IP = helpers.get_local_ip()

    LIGHT_SENSOR_VALUE = CONTENTS.get('light sensor value')
    LIGHT_SENSOR_KEY = CONTENTS.get('light sensor key')
    FILE_EXISTS = os.path.isfile(als_parser.CONF_FILE)
    parser = als_parser.RSyslogParser()

    if not FILE_EXISTS:
        open(als_parser.CONF_FILE, 'a').close()

    FILE_SIZE = os.path.getsize(als_parser.CONF_FILE)

    if not FILE_SIZE:
        ip_address = input("Log ALS values of ip: ")
        als_parser.add_ip_client(ip_address)

    f = subprocess.Popen(['tail', '-F', als_parser.SYSLOG_FILE],
                         stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p = select.poll()
    p.register(f.stdout)

    # als_parser.assign_groupaddresses("10.110.16.59", "1/1/20", "/1/1/21")

    while True:
        # TODO: Create a class "Phone" an create an instance of it for each client in
        # '/etc/rsyslog.d/als_snom.conf' 
    
        if p.poll(0.1):
            last_message = f.stdout.readline()
            last_message = last_message.decode('utf-8')

            if LIGHT_SENSOR_VALUE in last_message:
                message = parser.get_message(
                    last_message, LIGHT_SENSOR_VALUE)
                raw_value = message.get('value')
                value = als_parser.to_lux(raw_value)

                als_parser.save_als_value(value, raw_value)
                requests.post(
                    "http://localhost:8000/knx/values",
                    data={
                        "mac_address": als_parser.get_phones_info()[0].get("MAC"),
                        "ip_address": als_parser.get_phones_info()[0].get("IP"),
                        "raw_value": raw_value,
                        "value":  value
                    }
                )

                if knx_monitor.get_status('1/1/20') == 'on':
                    if value < 100:
                        try:
                            requests.get(f'http://{ GATEWAY_IP }:1234/1/1/21-plus')
                        except:
                            print(
                                'KNX gateway not reachable or invalid groupaddress/value')

                    elif value > 110:
                        try:
                            requests.get(f'http://{ GATEWAY_IP }:1234/1/1/21-minus')
                        except:
                            print('KNX gateway not reachable or invalid groupaddress/value')

        time.sleep(0.1)


if __name__ == "__main__":
    main()
