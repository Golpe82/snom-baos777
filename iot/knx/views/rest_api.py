import logging
import asyncio

from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, render

from knx.models import TemperatureRelation, AmbientLightRelation, Groupaddress, Supbrocess
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

    try:
        pid = Supbrocess.objects.get(name=f"blink_{groupaddress}").pid
    except Supbrocess.DoesNotExist:
        if "snom" in request.META["HTTP_USER_AGENT"]:
            context = {"text": f"No running blink subprocess for {groupaddress}"}
            return render(
                request, "knx/minibrowser/ip_phone_text.xml", context, content_type="text/xml"
            )
        return redirect(f"{settings.KNX_ROOT}subprocesses/")

    asyncio.run(kill_subprocess(pid))
    logging.error(f"Killed blink subprocess for groupaddress {groupaddress} with PID {pid}")
    Supbrocess.objects.get(name=f"blink_{groupaddress}").delete()
    writer = baos_ws.KNXWriteWebsocket(USERNAME, PASSWORD)
    writer.baos_interface.send_value(groupaddress, "off")

    if "snom" in request.META["HTTP_USER_AGENT"]:
        context = {"text": f"{groupaddress} stopped to blink"}
        return render(
            request, "knx/minibrowser/ip_phone_text.xml", context, content_type="text/xml"
        )

    return redirect(f"{settings.KNX_ROOT}subprocesses/")

def start_blink(request, main, midd, sub, sec_for_true, sec_for_false):
    dpt1 = ("DPST-1-1", "DPT-1")
    groupaddress = f"{main}/{midd}/{sub}"
    datapoint_type = Groupaddress.objects.get(address=groupaddress).datapoint_type

    if datapoint_type not in dpt1:
        message = f"Blinking only possible with dpt1 groupaddresses.\n Groupaddress {groupaddress} is dpt {datapoint_type}"
        logging.error(message)
        return HttpResponse(message)
    
    kill_groupaddress_blink_subprocesses(groupaddress)
    coroutine = prepare_blink_coroutine(groupaddress, sec_for_true, sec_for_false, USERNAME, PASSWORD)
    asyncio.run(coroutine)

    if "snom" in request.META["HTTP_USER_AGENT"]:
        context = {"text": f"{groupaddress} started to blink"}
        return render(
            request, "knx/minibrowser/ip_phone_text.xml", context, content_type="text/xml"
        )

    return redirect(f"{settings.KNX_ROOT}subprocesses/")

def kill_groupaddress_blink_subprocesses(groupaddress):
    subprocesses = Supbrocess.objects.filter(name=f"blink_{groupaddress}")
    for subprocess in subprocesses:
        asyncio.run(kill_subprocess(subprocess.pid)) 
        subprocess.delete()

async def kill_subprocess(pid):
    await asyncio.create_subprocess_exec("kill", "-9", str(pid))

async def prepare_blink_coroutine(groupaddress, sec_for_on, sec_for_off, user, password):
    subprocess = await asyncio.create_subprocess_exec(
        "python3", f"{settings.BASE_DIR}/knx/blink.py", groupaddress,
        str(sec_for_on), str(sec_for_off), user, password
    )
    await Supbrocess.objects.acreate(type="blink", name=f"blink_{groupaddress}", pid=subprocess.pid)

    logging.info(f"Started blink coroutine for groupaddress {groupaddress} with PID {subprocess.pid}")
