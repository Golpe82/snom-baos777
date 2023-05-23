import logging
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponse

from knx.models import TemperatureRelation, AmbientLightRelation
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

    if "snom" in request.META['HTTP_USER_AGENT']:
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
    else:
        return HttpResponse(value)

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
    ips_phone_model = AmbientLightRelation.objects.all().values_list("ip_address", "phone_model")
    data = {
        ip_phone_model[0]: ip_phone_model[1]
        for ip_phone_model in ips_phone_model
    }

    return JsonResponse(data)

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
