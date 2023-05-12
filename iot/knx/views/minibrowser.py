
import sys
import logging

from django.conf import settings
from django.shortcuts import render

from knx.models import Groupaddress

sys.path.append("..")

import baos777.baos_websocket as baos_ws

BAOS_USERNAME = "admin"
BAOS_PASSWORD = "admin"

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
    for a, b in subaddresses.items():
        logging.error(b)

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
    context = {
        "knx_gateway": settings.KNX_ROOT,
        "groupaddress": groupaddress,
        "groupaddress_name": groupaddress_data.name
    }
    return render(request, "knx/minibrowser/knx_values.xml", context, content_type="text/xml")
