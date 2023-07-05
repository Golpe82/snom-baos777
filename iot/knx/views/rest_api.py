import logging
import signal
import os
from contextlib import suppress

import asyncio

from django.http import JsonResponse, HttpResponse

from knx.models import TemperatureRelation, AmbientLightRelation, Groupaddress
import baos777.baos_websocket as baos_ws

USERNAME = "admin"
PASSWORD = "admin"

POST_RESPONSE = {"POST": "OK"}
logging.basicConfig(level=logging.DEBUG)


def knx_read(request, main, midd, sub):
    groupaddress = f"{main}/{midd}/{sub}"
    reader = baos_ws.KNXReadWebsocket(USERNAME, PASSWORD)
    value = reader.baos_interface.read_value(groupaddress)

    if "snom" in request.META["HTTP_USER_AGENT"]:
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
    ips_phone_model = TemperatureRelation.objects.all().values_list(
        "ip_address", "phone_model"
    )
    data = {ip_phone_model[0]: ip_phone_model[1] for ip_phone_model in ips_phone_model}

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
    ips_phone_model = AmbientLightRelation.objects.all().values_list(
        "ip_address", "phone_model"
    )
    data = {ip_phone_model[0]: ip_phone_model[1] for ip_phone_model in ips_phone_model}

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
        "dimm status groupaddress": relations.knx_dimm_status_address,
    }

    return JsonResponse(data)


def stop_blink(request, main, midd, sub):
    groupaddress = f"{main}/{midd}/{sub}"
    groupaddress_data = Groupaddress.objects.get(address=groupaddress)
    asyncio.run(stop_subprocess())

    return HttpResponse(f"{groupaddress_data.name} stopped to blink")

async def stop_subprocess():
    subprocess = await asyncio.create_subprocess_exec("kill", "-9", "6119")
    logging.error("stopped")

def start_blink(request, main, midd, sub, sec_for_true, sec_for_false):
    groupaddress = f"{main}/{midd}/{sub}"
    groupaddress_data = Groupaddress.objects.get(address=groupaddress)
    datapoint_type = groupaddress_data.datapoint_type
    is_dpt1 = datapoint_type == "DPST-1-1" or "DPT-1"

    if not is_dpt1:
        message = f"Blinking only possible with dpt1 groupaddresses.\n Groupaddress {groupaddress} is dpt {datapoint_type}"
        logging.error(message)
        return HttpResponse(message)

    writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
    asyncio.run(start_subprocess())

    return HttpResponse(f"{groupaddress_data.name} started to blink")

async def start_subprocess():
    subprocess = await asyncio.create_subprocess_exec("python3", "iot/knx/views/blink.py")
    logging.error(subprocess.pid)
