from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
import logging

from knx.models import Groupaddress, FunctionKeyLEDSubscriptions
import baos777.baos_websocket as baos_ws

BAOS_USERNAME = "admin"
BAOS_PASSWORD = "admin"

DATAPOINTS = {
    "DPT-1": {"action": "write", "function": "switch", "values": ["on", "off"]},
    "DPST-1-1": {"action": "write", "function": "switch", "values": ["on", "off"]},
    "DPST-1-11": {"action": "read", "function": "status", "values": []},
    "DPT-3": {
        "action": "write",
        "function": "dimming",
        "values": ["increase", "decrease"],
    },
    "DPST-3-7": {
        "action": "write",
        "function": "dimming",
        "values": ["increase", "decrease"],
    },
    "DPT-5": {
        "action": "write",
        "function": "scaling",
        "values": ["increase", "decrease"],
    },
    "DPST-5-1": {
        "action": "write",
        "function": "scaling",
        "values": ["increase", "decrease"],
    },
}


def minibrowser(request):
    mainaddresses = [
        maingroup[0]
        for maingroup in Groupaddress.objects.values_list("maingroup").distinct()
    ]
    context = {"knx_gateway": settings.KNX_ROOT, "mainaddresses": mainaddresses}
    template_data = _get_template_data(request, "knx_mainaddresses.xml")
    template = template_data.get("template")
    context["encoding"] = template_data.get("encoding")

    return render(
        request, f"knx/minibrowser/{template}", context, content_type="text/xml"
    )


def minibrowser_middaddresses(request, mainaddress):
    middaddresses = [
        middaddress
        for middaddress in Groupaddress.objects.filter(maingroup=mainaddress)
        .values_list("subgroup", flat=True)
        .distinct()
    ]
    context = {
        "knx_gateway": settings.KNX_ROOT,
        "mainaddress": mainaddress,
        "middaddresses": middaddresses,
    }
    template_data = _get_template_data(request, "knx_middaddresses.xml")
    template = template_data.get("template")
    context["encoding"] = template_data.get("encoding")

    return render(
        request, f"knx/minibrowser/{template}", context, content_type="text/xml"
    )


def minibrowser_subaddresses(request, mainaddress, middaddress):
    reader = baos_ws.KNXReadWebsocket(BAOS_USERNAME, BAOS_PASSWORD)
    baos_response = reader.baos_interface.sending_groupaddresses.values()
    subaddresses = {
        groupaddress.get("alias"): {
            groupaddress.get("address"): reader.baos_interface.read_value(
                groupaddress.get("address")
            )
        }
        for groupaddress in Groupaddress.objects.filter(
            address__in=baos_response, maingroup=mainaddress, subgroup=middaddress
        ).values("alias", "address")
    }

    context = {
        "knx_gateway": settings.KNX_ROOT,
        "mainaddress": mainaddress,
        "middaddress": middaddress,
        "subaddresses": subaddresses,
    }
    template_data = _get_template_data(request, "knx_subaddresses.xml")
    template = template_data.get("template")
    context["encoding"] = template_data.get("encoding")

    return render(
        request, f"knx/minibrowser/{template}", context, content_type="text/xml"
    )


def minibrowser_values(request, mainaddress, middaddress, subaddress):
    groupaddress = f"{mainaddress}/{middaddress}/{subaddress}"
    groupaddress_data = Groupaddress.objects.get(address=groupaddress)

    scaling = ["DPT-5", "DPST-5-1"]

    if groupaddress_data.datapoint_type in scaling:
        return HttpResponse(
            f"""
            <SnomIPPhoneInput track=no>
                <InputItem>
                    <DisplayName>Enter value in % for groupaddress {groupaddress}</DisplayName>
                    <InputToken>__Y__</InputToken>
                    <InputFlags>n</InputFlags>
                </InputItem>
                <Url>{settings.KNX_ROOT}write/{mainaddress}/{middaddress}/{subaddress}/scaling/__Y__</Url>
            </SnomIPPhoneInput>
        """,
            content_type="text/xml",
        )

    datapoint_data = DATAPOINTS.get(groupaddress_data.datapoint_type, {})
    callback_url = f"{settings.KNX_ROOT}minibrowser/{groupaddress_data.maingroup}/{groupaddress_data.subgroup}/"
    reader = baos_ws.KNXReadWebsocket(BAOS_USERNAME, BAOS_PASSWORD)
    current_status = reader.baos_interface.read_value(groupaddress)

    context = {
        "knx_gateway": settings.KNX_ROOT,
        "groupaddress": groupaddress,
        "groupaddress_name": groupaddress_data.name,
        "action": datapoint_data.get("action"),
        "function": datapoint_data.get("function"),
        "values": datapoint_data.get("values"),
        "callback_url": callback_url,
        "status": current_status,
    }

    template_data = _get_template_data(request, "knx_values.xml")
    template = template_data.get("template")
    context["encoding"] = template_data.get("encoding")

    return render(
        request, f"knx/minibrowser/{template}", context, content_type="text/xml"
    )


def minibrowser_led_subscription(request, subscription_id, boolean):
    subscription = FunctionKeyLEDSubscriptions.objects.get(id=subscription_id)
    led_update_xml = subscription.__getattribute__(f"on_change_xml_for_{boolean}")
    values = ["on", "off"]

    if boolean in values:
        return HttpResponse(led_update_xml, content_type="text/xml")

    template_data = _get_template_data(request)
    context = {
        "text": f"Wrong led subscription value {boolean}",
        "encoding": template_data.get("encoding"),
    }
    return render(request, context, content_type="text/xml")


def _get_template_data(request, base_template=None):
    http_agent = request.META["HTTP_USER_AGENT"]

    return {
        "encoding": "iso-8859-10" if "snomM" in http_agent else "utf-8",
        "template": f"dect/{base_template}" if "snomM" in http_agent else base_template,
    }
