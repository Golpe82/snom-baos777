"""Views for app knx"""
import os
import subprocess
import logging
import requests
from requests.auth import HTTPDigestAuth, HTTPBasicAuth
from time import sleep

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse

from knx import upload
from knx.models import (
    BrightnessRules,
    KnxMonitor,
    KnxStatus,
    Groupaddress,
    FunctionKeyLEDSubscriptions,
)
from knx.forms import AlsFormSet

APP = "KNX"
logging.basicConfig(level=logging.DEBUG)

import sys

sys.path.append("..")

import baos777.baos_websocket as baos_ws

USERNAME = "admin"
PASSWORD = "admin"


def index(request):
    if "snom" in request.META['HTTP_USER_AGENT']:
        return redirect(f"{settings.KNX_ROOT}minibrowser/")

    addresses_groups = {
        maingroup[0]: {
            item.subgroup
            for item in Groupaddress.objects.filter(maingroup=maingroup[0])
        }
        for maingroup in Groupaddress.objects.values_list("maingroup").distinct()
    }

    context =  {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Groupaddresses",
        "addresses_groups": addresses_groups,
        "knx_gateway": settings.KNX_ROOT,
        "gateway_ip": settings.GATEWAY_IP,
    }
    return render(request, "knx/addresses_groups.html", context)

DATAPOINT_TYPE_NAMES = ["switch", "dimming", "scaling", "value_temp"]


def knx_write(request, main, midd, sub, dpt_name, value):
    if dpt_name not in DATAPOINT_TYPE_NAMES:
        logging.error(f"Datapoint type name {dpt_name} not supported")
        return HttpResponse()

    groupaddress = f"{main}/{midd}/{sub}"

    if value == "phone_input":
        return HttpResponse(
            f"""
            <SnomIPPhoneInput track=no>
                <InputItem>
                    <DisplayName>Enter value in % for groupaddress {groupaddress}</DisplayName>
                    <InputToken>__Y__</InputToken>
                    <InputFlags>n</InputFlags>
                </InputItem>
                <Url>http://{settings.GATEWAY_IP}:8000/knx/write/{main}/{midd}/{sub}/scaling/__Y__</Url>
            </SnomIPPhoneInput>
        """,
            content_type="text/xml",
        )
    if dpt_name == "scaling" and int(value) not in range(101):
        return HttpResponse(
            """
                <SnomIPPhoneText>
                    <Text>Input not in range 0...100</Text>
                    <fetch mil=1500>snom://mb_exit</fetch>
                </SnomIPPhoneText>
            """,
            content_type="text/xml",
        )

    address_info = Groupaddress.objects.filter(address=groupaddress)
    address_code = address_info.values_list("code", flat=True).first()

    if address_code:
        if "snom" in request.META['HTTP_USER_AGENT']:
            return HttpResponse(
                f"""
                <SnomIPPhoneInput track=no>
                    <InputItem>
                        <DisplayName>Enter code for {groupaddress}</DisplayName>
                        <InputToken>__Y__</InputToken>
                        <InputFlags>p</InputFlags>
                    </InputItem>
                    <Url>{settings.KNX_ROOT}check_write/{main}/{midd}/{sub}/{value}/__Y__</Url>
                </SnomIPPhoneInput>
            """,
                content_type="text/xml",
            )
        
        return HttpResponse(f"{groupaddress} needs a code. Input only over a snom device possible, not over browser.")

    else:
        writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
        writer.baos_interface.send_value(groupaddress, value)

    return HttpResponse()


def check_code(request, main, midd, sub, value, code):
    groupaddress = f"{main}/{midd}/{sub}"
    address_info = Groupaddress.objects.filter(address=groupaddress)
    expected_code = address_info.values_list("code", flat=True).first()

    if code != expected_code:
        return HttpResponse(
            """
            <SnomIPPhoneText>
                <Text>Wrong code</Text>
                <fetch mil=1500>snom://mb_exit</fetch>
            </SnomIPPhoneText>
            """,
            content_type="text/xml",
        )

    writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
    writer.baos_interface.send_value(groupaddress, value)

    return HttpResponse()


def update_led_subscriptors(request, main, midd, sub, status):
    groupaddress = f"{main}/{midd}/{sub}"
    subscripted_leds = FunctionKeyLEDSubscriptions.objects.filter(
        knx_subscription=groupaddress
    )
    phone_wui_user = "admin"
    phone_wui_passwd = "7666"

    if subscripted_leds:
        logging.error(f"{status} updating snom led subscriptors {subscripted_leds}")
        for led in subscripted_leds:
            if status == "off":
                try:
                    response = requests.get(led.on_change_xml_for_off_url, timeout=5)
                except requests.exceptions.ConnectionError:
                    logging.error(
                        f"Target not reachable: {led.on_change_xml_for_off_url}"
                    )

                else:
                    if response.status_code == 401:
                        response = requests.get(
                            led.on_change_xml_for_off_url,
                            auth=HTTPDigestAuth(phone_wui_user, phone_wui_passwd),
                        )
                        if response.status_code == 401:
                            requests.get(
                                led.on_change_xml_for_off_url,
                                auth=HTTPBasicAuth(phone_wui_user, phone_wui_passwd),
                            )
            elif status == "on":
                try:
                    response = requests.get(led.on_change_xml_for_on_url, timeout=5)
                except requests.exceptions.ConnectionError:
                    logging.error(
                        f"Target not reachable: {led.on_change_xml_for_on_url}"
                    )
                else:
                    if response.status_code == 401:
                        response = requests.get(
                            led.on_change_xml_for_on_url,
                            auth=HTTPDigestAuth(phone_wui_user, phone_wui_passwd),
                        )
                        if response.status_code == 401:
                            requests.get(
                                led.on_change_xml_for_on_url,
                                auth=HTTPBasicAuth(phone_wui_user, phone_wui_passwd),
                            )
            else:
                logging.error(f"wrong value {status} for groupaddress {groupaddress}")
            sleep(1)

    return HttpResponse()


def addresses(request, maingroup, subgroup):
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    baos_response = reader.baos_interface.sending_groupaddresses.values()
    groupaddresses = Groupaddress.objects.filter(address__in=baos_response, maingroup=maingroup, subgroup=subgroup)
    context = {
        "app": APP,
        "page": f"{maingroup} {subgroup}",
        "groupaddresses": groupaddresses,
    }

    return render(request, "knx/groupaddresses.html", context)

def upload_file(request):
    context = {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Upload",
        "message": upload.process_file(request),
    }

    return render(request, "knx/upload.html", context)


def render_sensor_values(request):
    if request.method == "POST":
        message = "No post requests allowed"
        logging.warning(message)
    else:
        message = "Ambientlight sensor values"

    form = AlsFormSet()

    context = {"form": form, "message": message}

    return render(request, "knx/sensors_values.html", context)


def render_groupaddresses(request):
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    baos_response = reader.baos_interface.sending_groupaddresses.values()
    baos_sending_groupaddresses = Groupaddress.objects.filter(address__in=baos_response)
    other_groupaddresses = Groupaddress.objects.exclude(address__in=baos_response)

    context = {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Groupaddresses data",
        "baos_groupaddresses": baos_sending_groupaddresses,
        "other_groupaddresses": other_groupaddresses
    }

    return render(request, "knx/groupaddresses_data.html", context)


def get_rules(request):
    rules = BrightnessRules.objects.filter(mac_address="000413A34795").values(
        "min_value", "max_value"
    )

    return HttpResponse(rules)


def dect_ule(request):
    CMD_ROOT = "/usr/local/opend/openD/dspg/base/ule-hub/"
    INTERPRETER = "python3"
    command = request.GET.get("cmd")

    if command:
        process = subprocess.run(f"{INTERPRETER} { CMD_ROOT }{command}", shell=True)
        logging.info(f"Command { command } sent")
        logging.info(f"Returncode: { process.returncode }")

    context = {
        "command": f"{INTERPRETER} { CMD_ROOT }{command}",
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "DECT ULE",
    }

    return render(request, "knx/dect_ule.html", context)


def knx_monitor(request):
    monitor = KnxMonitor.objects.all()

    context = {
        "monitor": monitor.values,
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "MONITOR",
    }

    return render(request, "knx/knx_monitor.html", context)


def knx_status(request):
    status = KnxStatus.objects.all()

    context = {
        "status": status,
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "STATUS",
    }

    return render(request, "knx/knx_status.html", context)
