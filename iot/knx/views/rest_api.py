import logging
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from knx.models import KnxStatus, AlsStatus, KnxMonitor, TemperatureRelation, AmbientLightRelation
import sys

sys.path.append("/usr/local/gateway")

import baos777.baos_websocket as baos_ws

USERNAME = "admin"
PASSWORD = "admin"

POST_RESPONSE = {"POST": "OK"}
logging.basicConfig(level=logging.DEBUG)


def knx_read(request, main, midd, sub):
    groupaddress = f"{main}/{midd}/{sub}"
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    value = reader.baos_interface.read_value(groupaddress)

    return HttpResponse(
        f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <SnomIPPhoneText>
            <Text>Groupaddress {groupaddress} has status {value}</Text>
            <fetch mil=3000>snom://mb_exit</fetch>
            </SnomIPPhoneText>
        """,
            content_type="text/xml",
        )

def temperature_sensor_relations_ips(request):
    ips_phone_model = TemperatureRelation.objects.all().values_list("ip_address", "phone_model")
    data = {
        ip_phone_model[0]: ip_phone_model[1]
        for ip_phone_model in ips_phone_model
    }

    return JsonResponse(data)

def temperature_sensor_relations(request, device_ip):
    relations = TemperatureRelation.objects.get(ip_address=device_ip)
    data = {
        "device ip": relations.ip_address,
        "phone type": relations.phone_model,
        "phone location": relations.phone_location,
        "send celsius groupaddress": relations.knx_send_celsius_address,
        "celsius delta": relations.celsius_delta,
    }

    return JsonResponse(data)

def ambient_light_sensor_relations_ips(request):
    ips = AmbientLightRelation.objects.all().values_list('ip_address', flat=True)

    return JsonResponse(list(ips), safe=False)

def ambient_light_sensor_relations(request, device_ip):
    relations = AmbientLightRelation.objects.get(ip_address=device_ip)
    data = {
        "device ip": relations.ip_address,
        "phone type": relations.phone_model,
        "phone location": relations.phone_location,
        "send lux groupaddress": relations.knx_send_lux_address,
        "lux delta": relations.lux_delta,
        "switch groupaddress": relations.knx_switch_address,
        "min lux value": relations.min_lux,
        "max lux value": relations.max_lux,
        "dimm groupaddress": relations.knx_dimm_address,
        "dimm status groupaddress": relations.knx_dimm_status_address
    }

    return JsonResponse(data)


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
