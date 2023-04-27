import logging
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from knx.models import KnxStatus, AlsStatus, KnxMonitor
import sys

sys.path.append("usr/local/gateway")

import baos777.baos_websocket as baos_ws

USERNAME = "admin"
PASSWORD = "admin"

POST_RESPONSE = {"POST": "OK"}
logging.basicConfig(level=logging.DEBUG)


def get_groupaddress_status(request, main, midd, sub):
    request_address = f"{main}/{midd}/{sub}"
    status_object = KnxStatus.objects.filter(groupaddress=request_address).latest("status")

    logging.info(f"Status of { status_object.groupaddress }: { status_object.status }")

    data = {
        "Groupaddress": status_object.groupaddress,
        "Status": status_object.status
    }

    return JsonResponse(data)

def knx_read(request, main, midd, sub):
    groupaddress = f"{main}/{midd}/{sub}"
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    value = reader.baos_interface.read_value(groupaddress)

    return HttpResponse(
        f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <SnomIPPhoneText>
            <Text>Groupaddress {groupaddress} has status {value}</Text>
            <fetch mil=1500>snom://mb_exit</fetch>
            </SnomIPPhoneText>
        """,
            content_type="text/xml",
        )
@csrf_exempt
def post_sensor_value(request):
    device_mac = request.POST.get("mac_address")
    obj, created = AlsStatus.objects.update_or_create(
        mac_address = device_mac,
        defaults = {
            "ip_address": request.POST.get("ip_address"),
            "raw_value": request.POST.get("raw_value"),
            "value": request.POST.get("value"),
            "time_stamp": datetime.now()
        }
    )
    logging.info(f"als value for mac {device_mac} created = {created}, updated to {obj.value} Lux")

    return JsonResponse(POST_RESPONSE)

@csrf_exempt
def post_knx_status(request):
    logging.info(f"groupaddress {request.POST.get('groupaddress')} status to save {request.POST.get('status')}")
    obj, _created = KnxStatus.objects.update_or_create(
        groupaddress_name=request.POST.get("groupaddress_name"),
        groupaddress=request.POST.get("groupaddress"),
        defaults={
            "status": request.POST.get("status"),
            "timestamp": datetime.now()
        }
    )
    logging.info(f"{obj.groupaddress_name}: {obj.status}")

    return JsonResponse(POST_RESPONSE)

# not in use, too much traffic
@csrf_exempt
def post_knx_monitor(request):
    if KnxMonitor.objects.count() > 2000:
        first = KnxMonitor.objects.first().id
        KnxMonitor.objects.filter(id=first).delete()
    logging.info(request.POST.get("raw_frame"))

    KnxMonitor.objects.create(
        groupaddress_name=request.POST.get("groupaddress_name"),
        groupaddress=request.POST.get("groupaddress"),
        datapoint_type=request.POST.get("datapoint_type"),
        status=request.POST.get("status"),
        raw_frame=request.POST.get("raw_frame")
    )

    return JsonResponse(POST_RESPONSE)
