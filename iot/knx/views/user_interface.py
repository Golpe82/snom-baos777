"""Views for app knx"""
import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse

from knx import upload
from knx.http_dispatcher import HTTPKNXDispatcher
from knx.models import Groupaddress, FunctionKeyLEDBoolRelation, Supbrocess,Setting
import baos777.baos_websocket as baos_ws

APP = "KNX"
logging.basicConfig(level=logging.DEBUG)

USERNAME = "admin"
PASSWORD = "admin"


def index(request):
    if "snom" in request.META["HTTP_USER_AGENT"]:
        return redirect(f"{settings.KNX_ROOT}minibrowser/")

    addresses_groups = {
        maingroup[0]: {
            item.subgroup
            for item in Groupaddress.objects.filter(maingroup=maingroup[0])
        }
        for maingroup in Groupaddress.objects.values_list("maingroup").distinct()
    }
    context = {
        "app": APP,
        "addresses_groups": addresses_groups,
    }

    return render(request, "knx/addresses_groups.html", context)


DATAPOINT_TYPE_NAMES = ["switch", "dimming", "scaling", "value_temp"]


def knx_write(request, main, midd, sub, dpt_name, value):
    if dpt_name not in DATAPOINT_TYPE_NAMES:
        logging.error(f"Datapoint type name {dpt_name} not supported")
        return HttpResponse()

    groupaddress = f"{main}/{midd}/{sub}"
    address_info = Groupaddress.objects.filter(address=groupaddress)
    address_code = address_info.values_list("code", flat=True).first()

    if address_code:
        if "snom" in request.META["HTTP_USER_AGENT"]:
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

        return HttpResponse(
            f"{groupaddress} needs a code. Input only over a snom device possible, not over browser."
        )

    if dpt_name == "scaling" and value == "phone_input":
        return HttpResponse(
            f"""
            <SnomIPPhoneInput track=no>
                <InputItem>
                    <DisplayName>Enter value in % for groupaddress {groupaddress}</DisplayName>
                    <InputToken>__Y__</InputToken>
                    <InputFlags>n</InputFlags>
                </InputItem>
                <Url>{settings.KNX_ROOT}write/{main}/{midd}/{sub}/scaling/__Y__</Url>
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
    if dpt_name == "switch" and value == "toggle":
        reader = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
        is_on = reader.baos_interface.read_raw_value(groupaddress)
        value = "off" if is_on else "on"

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
    subscripted_leds = FunctionKeyLEDBoolRelation.objects.filter(
        write_groupaddress=groupaddress
    )

    if subscripted_leds:
        http_dispatcher = HTTPKNXDispatcher(subscripted_leds, status, groupaddress)
        http_dispatcher.dispatch()
    else:
        logging.info(f"No LED subscriptors for groupaddress {groupaddress}")

    return HttpResponse()


def addresses(request, maingroup, subgroup):
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    baos_response = reader.baos_interface.sending_groupaddresses.values()
    groupaddresses = Groupaddress.objects.filter(
        address__in=baos_response, maingroup=maingroup, subgroup=subgroup
    )
    context = {
        "app": APP,
        "page": f"{maingroup} {subgroup}",
        "groupaddresses": groupaddresses,
    }

    return render(request, "knx/groupaddresses.html", context)


def upload_file(request):
    context = {
        "app": APP,
        "message": upload.process_file(request),
    }

    return render(request, "knx/upload.html", context)


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
        "other_groupaddresses": other_groupaddresses,
    }

    return render(request, "knx/groupaddresses_data.html", context)

def subprocesses(request, message=""):
    subprocesses = Supbrocess.objects.all()
    context = {
        "app": APP,
        "subprocesses": subprocesses,
    }

    return render(request, "knx/subprocesses.html", context)

def knx_settings(request):
    settings = {"baos ip": Setting.objects.all().first().baos777_ip_address}
    logging.error(settings)
    return JsonResponse(settings)