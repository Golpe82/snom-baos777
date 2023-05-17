
import sys

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from knx.models import Groupaddress

sys.path.append("..")

import baos777.baos_websocket as baos_ws

BAOS_USERNAME = "admin"
BAOS_PASSWORD = "admin"

DATAPOINTS = {
    "DPT-1": {
        "action": "write",
        "function": "switch",
        "values": ["on", "off"]
    },
    "DPST-1-1": {
        "action": "write",
        "function": "switch",
        "values": ["on", "off"]
    },
    "DPST-1-11": {
        "action": "read",
        "function": "status",
        "values": []
    },
    "DPT-3": {
        "action": "write",
        "function": "dimming",
        "values": ["increase", "decrease"]
    },
    "DPST-3-7": {
        "action": "write",
        "function": "dimming",
        "values": ["increase", "decrease"]
    },
    "DPT-5": {
        "action": "write",
        "function": "scaling",
        "values": ["increase", "decrease"]
    },
    "DPST-5-1": {
        "action": "write",
        "function": "scaling",
        "values": ["increase", "decrease"]
    },
}

def minibrowser(request):
    mainaddresses = [
        maingroup[0]
        for maingroup in Groupaddress.objects.values_list("maingroup").distinct()
    ]
    context =  {
        "knx_gateway": settings.KNX_ROOT,
        "mainaddresses": mainaddresses,
    }

    return render(request, "knx/minibrowser/knx_mainaddresses.xml", context, content_type="text/xml")

def minibrowser_middaddresses(request, mainaddress):
    middaddresses = [
        middaddress
        for middaddress in Groupaddress.objects.filter(maingroup=mainaddress).values_list("subgroup", flat=True).distinct()
    ]
    context = {
        "knx_gateway": settings.KNX_ROOT,
        "mainaddress": mainaddress,
        "middaddresses": middaddresses
    }

    return render(request, "knx/minibrowser/knx_middaddresses.xml", context, content_type="text/xml")

def minibrowser_subaddresses(request, mainaddress, middaddress):
    reader = baos_ws.KNXReadWebsocket(BAOS_USERNAME, BAOS_PASSWORD)
    baos_response = reader.baos_interface.sending_groupaddresses.values()
    subaddresses = {
        groupaddress.get("name"): {groupaddress.get("address"): reader.baos_interface.read_value(groupaddress.get("address"))}
        for groupaddress in Groupaddress.objects.filter(address__in=baos_response, maingroup=mainaddress, subgroup=middaddress).values("name", "address")
    }

    context = {
        "knx_gateway": settings.KNX_ROOT,
        "mainaddress": mainaddress,
        "middaddress": middaddress,
        "subaddresses": subaddresses
    }

    return render(request, "knx/minibrowser/knx_subaddresses.xml", context, content_type="text/xml")

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
                <Url>http://{settings.GATEWAY_IP}:8000/knx/write/{mainaddress}/{middaddress}/{subaddress}/scaling/__Y__</Url>
            </SnomIPPhoneInput>
        """,
            content_type="text/xml",
        )

    datapoint_data = DATAPOINTS.get(groupaddress_data.datapoint_type, {})
    callback_url =f"{settings.KNX_ROOT}minibrowser/{groupaddress_data.maingroup}/{groupaddress_data.subgroup}/"
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
        "status": current_status
        }

    return render(request, "knx/minibrowser/knx_values.xml", context, content_type="text/xml")
