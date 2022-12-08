#!/usr/bin/python3
# -*- coding: utf-8 -*-

from pyparsing import Word, hexnums, alphanums, Combine, nums, string, Regex
import subprocess
import re
import getmac
import requests
import logging


CONF_FILE = "/etc/rsyslog.d/als_snom.conf"
SYSLOG_FILE = "/usr/local/gateway/snomsyslogknx/als_snom.log"
MSG_KEYS = ["timestamp", "ip address", "mac", "syslog class", "snom class", "content"]
BOOTSTRAP = {
    "success": "alert-success",
    "info": "alert-info",
    "warning": "alert-warning",
    "danger": "alert-danger",
    "primary": "alert-primary",
    "secondary": "alert-secondary",
    "light": "alert-light",
    "dark": "alert-dark",
}

POST_STATUS_URL = "http://localhost:8000/knx/values"
# GET_RULES_URL = "http://localhost:8000/knx/rules/"
KNX_URL = "http://localhost:1234/"
DEVELOPMENT_GATEWAY_URL = "http://10.110.16.101:1234/"
STATUS_URL = "http://localhost:8000/knx/status/"
DEV_STATUS_URL = "http://10.110.16.101:8000/knx/status/"

logging.basicConfig(level=logging.INFO)


# TODO: REFACTOR

def add_ip_client(ip_address):
    MAC = str(getmac.get_mac_address(ip=ip_address)).replace(":", "")
    TEMPLATE = (
        f'$template snom{MAC}, "{ SYSLOG_FILE }"\n'
        f':fromhost-ip, isequal, "{ ip_address }" -?snom{MAC}\n'
        f"& stop\n"
    )

    with open(CONF_FILE, "a+") as als_log:
        content = als_log.readlines()

        if TEMPLATE not in content:
            als_log.write(TEMPLATE)

    subprocess.call(["systemctl", "restart", "rsyslog"])


def get_phones_info():
    IP = "\d+\.\d+\.\d+\.\d+"
    MAC = "00041[a-f0-9]+"
    phones = []
    PHONE_ITEM = {"IP": "no IP", "MAC": "no MAC"}

    with open(CONF_FILE) as syslog_config:
        phone_item = PHONE_ITEM

        for line in syslog_config:
            match_ip = re.search(IP, line)
            match_mac = re.search(MAC, line)

            if match_ip:
                phone_item.update(IP=match_ip.group(0))

            if match_mac:
                mac = match_mac.group(0)

                if mac in phone_item.get("MAC"):
                    phones.append(phone_item)
                    phone_item = PHONE_ITEM

                else:
                    phone_item.update(MAC=mac)

    return phones


def assign_groupaddresses(phone_ip, ga_read, ga_write):
    for phone_info in get_phones_info():
        if phone_info.get("IP") == phone_ip:
            phone_info.update(GA_READ=ga_read, GA_WRITE=ga_write)


def to_lux(raw_value):
    value = int(raw_value) * 6.5 / 100

    return round(value, 2)


class DBActions(object):
    def als_save(self, client_ip, client_mac, raw_value, value):
        try:
            requests.post(
                POST_STATUS_URL,
                data={
                    "mac_address": client_mac,
                    "ip_address": client_ip,
                    "raw_value": raw_value,
                    "value": value,
                },
            )

        except:
            logging.error(f"Could not save data with post. URL = {POST_STATUS_URL}")


class KNXActions(object):
    def __init__(self, client_info):
        self.client_label = client_info.get("label")
        self.client_min_brightness = client_info.get("min brightness")
        self.client_max_brightness = client_info.get("max brightness")
        self.switch_groupaddress = client_info.get("switch groupaddress")
        self.relative_dim_groupaddress = client_info.get("relative dim groupaddress")
        self.send_celsius_groupaddress = client_info.get("send celsius gropuaddress")

    def knx_dimm_relative(self, lux_value):
        if lux_value < self.client_min_brightness:
            self.knx_increase()
        elif lux_value > self.client_max_brightness:
            self.knx_decrease()

    def knx_increase(self):
        value = "-plus"
        logging.info(f"{self.client_label} dimming up {self.relative_dim_groupaddress}")

        try:
            requests.get(f"{KNX_URL}{self.relative_dim_groupaddress}{value}")
        except requests.exceptions.ConnectionError:
            logging.warning(f"Default localhost not reachable, trying {DEVELOPMENT_GATEWAY_URL}...")
            requests.get(f"{DEVELOPMENT_GATEWAY_URL}{self.relative_dim_groupaddress}{value}")
        except:
            logging.exception(
                f"Could not increase { self.relative_dim_groupaddress }. KNX gateway not reachable or invalid groupaddress/value"
            )

    def knx_decrease(self):
        value = "-minus"
        logging.info(f"{self.client_label} dimming down {self.relative_dim_groupaddress}")

        try:
            requests.get(f"{ KNX_URL }{ self.relative_dim_groupaddress }{ value }")
        except requests.exceptions.ConnectionError:
            logging.warning(f"Default localhost not reachable, trying {DEVELOPMENT_GATEWAY_URL}...")
            requests.get(f"{ DEVELOPMENT_GATEWAY_URL }{ self.relative_dim_groupaddress }{ value }")
        except:
            logging.exception(
                f"Could not decrease { self.relative_dim_groupaddress }. KNX gateway not reachable or invalid groupaddress/value"
            )

    def knx_send_celsius(self, celsius_value):
        logging.info(f"{self.client_label} sending celsius value to {self.send_celsius_groupaddress}")

        try:
            url = f"{KNX_URL}{self.send_celsius_groupaddress}-send_celsius={celsius_value}"
            logging.info(f"Trying to send url {url}...")
            requests.get(url)
        except requests.exceptions.ConnectionError:
            logging.warning(f"Default localhost not reachable, trying {DEVELOPMENT_GATEWAY_URL}...")
            url = f"{DEVELOPMENT_GATEWAY_URL}{self.send_celsius_groupaddress}-send_celsius={celsius_value}"
            logging.info(f"Trying to send url {url}...")
            requests.get(url)
        except:
            logging.exception(
                f"Could not send celsius value to {self.send_celsius_groupaddress}. KNX gateway not reachable or invalid groupaddress/value"
            )

    def get_status(self):
        try:
            status = requests.get(f"{STATUS_URL}{self.switch_groupaddress}/")

        except requests.exceptions.ConnectionError:
            logging.warning(f"Default localhost not reachable, trying {DEVELOPMENT_GATEWAY_URL}...")
            status = requests.get(f"{DEV_STATUS_URL}{self.switch_groupaddress}/")

        except:
            logging.exception(f"No status for groupaddress {self.switch_groupaddress}")
            raise

        return status.json().get("Status")


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
        # message = Regex(".*")

        # pattern build
        self.__pattern = (
            timestamp + ip_address + mac + syslog_class + snom_class + message
        )
        # print(self.__pattern)

    def tail(self, f, n, offset=0):
        # when tail fails, log file not existing we return an empty list
        lines = []
        with subprocess.Popen(
            ["tail", "-n", "%s" % (n + offset), f],
            stdout=subprocess.PIPE,
            encoding="utf-8",
        ) as proc:
            lines = proc.stdout.readlines()
            proc.wait()

        return lines

    def get_message(self, message, content):
        message_dict = self.to_dict(message)
        message_dict.update({"bootstrap": BOOTSTRAP.get("info")})
        content_value = self.get_content_value(message_dict)

        return self.update_message(message_dict, content_value)

    def to_dict(self, message):
        msg_values = self.__pattern.parseString(message)

        return dict(zip(MSG_KEYS, msg_values))

    def get_content_value(self, message):
        DIGITS = "\d+"
        CONTENT = message.get(MSG_KEYS[5])

        match = re.search(DIGITS, CONTENT)

        return match.group(0)

    def update_message(self, message, value):
        message.update({"bootstrap": BOOTSTRAP.get("success"), "value": value})

        return message
