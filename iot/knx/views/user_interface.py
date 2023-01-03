"""Views for app knx"""
import os
import subprocess
import logging

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from knx import upload
from knx.models import BrightnessRules, KnxMonitor, KnxStatus, Groupaddress
from knx.forms import AlsFormSet

APP = "KNX"
logging.basicConfig(level=logging.DEBUG)


def index(request):
    addresses_groups = {
        maingroup[0]: {item.subgroup for item in Groupaddress.objects.filter(maingroup=maingroup[0])}
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

def addresses(request, maingroup, subgroup):
    groupaddresses = Groupaddress.objects.filter(maingroup=maingroup, subgroup=subgroup)
    context = {
        "app": APP,
        "page": f"{maingroup} {subgroup}",
        "groupaddresses": groupaddresses
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

    context = {
        "form": form,
        "message": message
    }

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
