"""Views for app knx"""
import os
import subprocess
import logging
import requests
from requests.auth import HTTPDigestAuth
from time import sleep

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from knx import upload
from knx.models import BrightnessRules, KnxMonitor, KnxStatus, Groupaddress, FunctionKeyLEDSubscriptions
from knx.forms import AlsFormSet

APP = "KNX"
logging.basicConfig(level=logging.DEBUG)


def index(request):
    addresses_groups = {
        maingroup[0]: {
            item.subgroup
            for item in Groupaddress.objects.filter(maingroup=maingroup[0])
        }
        for maingroup in Groupaddress.objects.values_list("maingroup").distinct()
    }

    context = {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Groupaddresses",
        "addresses_groups": addresses_groups,
        "knx_gateway": settings.KNX_ROOT,
        "gateway_ip": settings.GATEWAY_IP,
    }

    return render(request, "knx/addresses_groups.html", context)


def knx_write(request, main, midd, sub, value):
    groupaddress = f"{main}/{midd}/{sub}"

    address_info = Groupaddress.objects.filter(address=groupaddress)
    address_code = address_info.values_list("code", flat=True).first()

    # address has a code
    if address_code:
        print(address_code)

        return HttpResponse(
            f"""
            <SnomIPPhoneInput track=no>
                <InputItem>
                    <DisplayName>Enter code for {groupaddress}</DisplayName>
                    <InputToken>__Y__</InputToken>
                    <InputFlags>p</InputFlags>
                </InputItem>
                <Url>http://{settings.GATEWAY_IP}:8000/knx/write/{main}/{midd}/{sub}/{value}/__Y__</Url>
            </SnomIPPhoneInput>
        """,
            content_type="text/xml",
        )

    if value == "on":
        value = "an"
        requests.get(f"{settings.KNX_ROOT}{groupaddress}-{value}")

        return HttpResponse(
            f"""
        <SnomIPPhoneText>
            <Text>Groupaddress {groupaddress} changed to {value}</Text>
            <LED number="5" color="green">On</LED>
            <LED number="6">Off</LED>
            <fetch mil=1500>snom://mb_exit</fetch>
        </SnomIPPhoneText>
        """,
            content_type="text/xml",
        )
    value = "aus"
    requests.get(f"{settings.KNX_ROOT}{groupaddress}-{value}")
    return HttpResponse(
        f"""
    <SnomIPPhoneText>
        <Text>Groupaddress {groupaddress} changed to {value}</Text>
        <LED number="5">Off</LED>
        <LED number="6" color="green">On</LED>
        <fetch mil=1500>snom://mb_exit&applyline</fetch>
    </SnomIPPhoneText>
    """,
        content_type="text/xml",
    )


def check_code(request, main, midd, sub, value, code):
    groupaddress = f"{main}/{midd}/{sub}"
    address_info = Groupaddress.objects.filter(address=groupaddress)

    # address has a code
    if code == address_info.values_list("code", flat=True).first():
        if value == "on":
            value = "an"
            requests.get(f"{settings.KNX_ROOT}{groupaddress}-{value}")
            return HttpResponse(
                f"""
            <SnomIPPhoneText>
                <Text>Groupaddress {groupaddress} changed to {value}</Text>
                <LED number="5" color="green">On</LED>
                <LED number="6">Off</LED>
                <fetch mil=1500>snom://mb_exit</fetch>
            </SnomIPPhoneText>
            """,
                content_type="text/xml",
            )

        value = "aus"
        requests.get(f"{settings.KNX_ROOT}{groupaddress}-{value}")

        return HttpResponse(
            f"""
        <SnomIPPhoneText>
            <Text>Groupaddress {groupaddress} changed to {value}</Text>
            <LED number="5">Off</LED>
            <LED number="6" color="green">On</LED>
            <fetch mil=1500>snom://mb_exit&applyline</fetch>
        </SnomIPPhoneText>
        """,
            content_type="text/xml",
        )

    return HttpResponse(
        """
        <SnomIPPhoneText>
            <Text>Wrong code</Text>
            <fetch mil=1500>snom://mb_exit</fetch>
        </SnomIPPhoneText>
        """,
        content_type="text/xml",
    )

def update_led_subscriptors(request, main, midd, sub, status):
    groupaddress = f"{main}/{midd}/{sub}"
    subscripted_leds = FunctionKeyLEDSubscriptions.objects.filter(knx_subscription=groupaddress)

    if subscripted_leds:
        logging.error(f"{status} updating snom led subscriptors {subscripted_leds}")
        for led in subscripted_leds:
            if status == "off":
                response = requests.get(led.on_change_xml_for_off_url)
                if response.status_code == 401:
                    logging.error(response.status_code)
                    r = requests.post(led.on_change_xml_for_off_url, auth=HTTPDigestAuth("admin", "7666"))
                    logging.error(r.status_code)
            elif status == "on":
                response = requests.get(led.on_change_xml_for_on_url)
                if response.status_code == 401:
                    logging.error(response.status_code)
                    r = requests.get(led.on_change_xml_for_on_url, auth=HTTPDigestAuth("admin", "7666"))
                    logging.error(r.status_code)
            else:
                logging.error(f"wrong value {status} for groupaddress {groupaddress}")
            sleep(3)

    return HttpResponse()

def addresses(request, maingroup, subgroup):
    groupaddresses = Groupaddress.objects.filter(maingroup=maingroup, subgroup=subgroup)
    context = {
        "app": APP,
        "page": f"{maingroup} {subgroup}",
        "groupaddresses": groupaddresses,
    }

    return render(request, "knx/groupaddresses.html", context)


def minibrowser(request):
    if os.path.exists(settings.XML_TARGET_PATH):
        return render(
            request, "knx/minibrowser.xml", content_type="application/xhtml+xml"
        )

    context = {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Minibrowser",
        "addresses": None,
        "knx_gateway": settings.KNX_ROOT,
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
    groupaddresses = Groupaddress.objects.all()

    context = {
        "project": settings.PROJECT_NAME,
        "app": APP,
        "page": "Groupaddresses data",
        "groupaddresses": groupaddresses,
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
