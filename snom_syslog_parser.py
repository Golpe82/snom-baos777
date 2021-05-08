#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd
from pyparsing import Word, hexnums, alphas, alphanums, Suppress, Combine, nums, string, Regex, pyparsing_common
import subprocess
import re


class RSyslogParser(object):
    """Class to parse snom desktop syslog files 
    e.g. 
    Feb 23 08:29:18.156 [DEBUG0] PHN: apply_value: hide_identity = 'false', set.need_apply: 0, finished: 1, need reboot to apply: 0

    Feb 24 16:20:08 10.110.16.59 000413A34795 [INFO  ] PHN: ALS_VALUE:180
    """

    def __init__(self):
        ints = Word(nums)

        # timestamp
        month = Word(string.ascii_uppercase, string.ascii_lowercase, exact=3)
        day = ints
        hour = Combine(ints + ":" + ints + ":" + ints)

        # still 3 fields in pattern
        timestamp = Combine(month + Regex("..") + day + " " + hour)

        ip_address = Combine(ints + "." + ints + "." + ints + "." + ints)

        # phone mac
        mac = Word(hexnums, exact=12)

        # syslog class
        syslog_class = Combine("[" + Word(alphanums) + Regex(".*]"))

        # snom class
        snom_class = Combine(Word(string.ascii_uppercase, exact=3) + ":")

        # message still has ending ']'
        message = Combine(Regex(".*"))
        #message = Regex(".*")

        # pattern build
        self.__pattern = timestamp + ip_address + \
            mac + syslog_class + snom_class + message
        # print(self.__pattern)

    def to_dict(self, message):
        MSG_KEYS = ["timestamp", "ip address", "mac",
                    "syslog class", "snom class", "message"]

        msg_values = self.__pattern.parseString(message)

        return dict(zip(MSG_KEYS, msg_values))

    def tail(self, f, n, offset=0):
        # when tail fails, log file not existing we return an empty list
        lines = []
        with subprocess.Popen(['tail', '-n', '%s' % (n + offset), f], stdout=subprocess.PIPE, encoding='utf-8') as proc:
            lines = proc.stdout.readlines()
            proc.wait()
        return lines

    def get_value(self, message, pattern=".*PP_.*"):
        match = re.search(pattern, message)

        if match:
            return match.group(0)

        return match

    def analyse_syslog_lines(self, syslogFileContent):
        # TODO: Split function. It makes several things, not only analyse
        SENSOR_PATTERN = ".*ALS_VALUE:.*"
        list1 = []
        for message_raw in syslogFileContent:
            message = self.to_dict(message_raw)
            message['severity'] = 'alert-info'
            sensor_value = self.get_value(
                message['message'], SENSOR_PATTERN)

            if sensor_value:
                NUMBERS = "\d+"
                match = re.search(NUMBERS, sensor_value)
                message['answer'] = match.group(0)
                message['severity'] = 'alert-success'
                print(message)
                list1.append(message)

        return list1
