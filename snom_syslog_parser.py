#!/usr/bin/python3
# -*- coding: utf-8 -*-

import pandas as pd
from pyparsing import Word, hexnums, alphas, alphanums, Suppress, Combine, nums, string, Regex, pyparsing_common
# import time
import subprocess
# import select


#from bottle_utils.i18n import lazy_ngettext as ngettext, lazy_gettext as _

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

    def parse(self, line):
        # print('line:',line)
        parsed = self.__pattern.parseString(line)

        # print(parsed)
        payload = {}
        payload["timestamp"] = parsed[0]
        payload["ip_address"] = parsed[1]
        payload["mac"] = parsed[2]
        payload["syslog_class"] = parsed[3]
        payload["snom_class"] = parsed[4]
        payload["message"] = parsed[5]

        return payload

    def tail(self, f, n, offset=0):
        # when tail fails, log file not existing we return an empty list
        lines = []
        with subprocess.Popen(['tail', '-n', '%s' % (n + offset), f], stdout=subprocess.PIPE, encoding='utf-8') as proc:
            lines = proc.stdout.readlines()
            proc.wait()
        return lines

    def grep_syslog(self, line, pattern=".*PP_.*"):
        try:
            # print(line)
            pattern = Regex(pattern)
            parsed = pattern.parseString(line)
            return(parsed)
        except:
            return False

    def analyse_syslog(self, file, num_lines=100):

        syslogFileContent = self.tail(file, num_lines)

        # print(syslogFileContent)
        list1 = []
        for line in syslogFileContent:
            fields = self.parse(line)
            # print(line)

            fields['severity'] = 'alert-info'
            append = False

            # ALS_VALUE:1071
            if self.grep_syslog(fields['message'], ".*ALS_VALUE:.*"):
                before = Regex('.*ALS_VALUE:')
                value = pyparsing_common.number
                after = Regex('.*')
                pattern = before + value + after
                parsed = pattern.parseString(fields['message'])
                # print(parsed[1])
                fields['answer'] = str(parsed[1])
                fields['severity'] = 'alert-success'
                append = True

            if append:
                list1.append(fields)

        return list1

    def analyse_syslog_lines(self, syslogFileContent):
        # print(syslogFileContent)
        list1 = []
        for line in syslogFileContent:
            fields = self.parse(line)
            # print(line)

            fields['severity'] = 'alert-info'
            append = False

            # ALS_VALUE:1071
            if self.grep_syslog(fields['message'], ".*ALS_VALUE:.*"):
                before = Regex('.*ALS_VALUE:')
                value = pyparsing_common.number
                after = Regex('.*')
                pattern = before + value + after
                parsed = pattern.parseString(fields['message'])
                # print(parsed[1])
                fields['answer'] = str(parsed[1])
                fields['severity'] = 'alert-success'
                append = True

            if append:
                list1.append(fields)

        return list1
