"""Views for app knx"""
import os
import csv
import subprocess
import requests

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from knx import groupaddresses, upload
from knx.models import AlsStatus

APP = 'KNX'

def index(request):
    data = None

    if os.path.exists(settings.CSV_SOURCE_PATH):
        data = groupaddresses.get_data()

    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Groupaddresses',
        'addresses': data,
        'knx_gateway': settings.KNX_ROOT,
        }

    return render(request, 'knx/groupaddresses.html', context)


def minibrowser(request):
    if os.path.exists(settings.XML_TARGET_PATH):
        return render(request, 'knx/minibrowser.xml', content_type="application/xhtml+xml")

    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Minibrowser',
        'addresses': None,
        'knx_gateway': settings.KNX_ROOT,
        }

    return render(request, 'knx/groupaddresses.html', context)

def upload_file(request):

    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Upload',
        'message': upload.process_file(request),
    }

    return render(request, 'knx/upload.html', context)


@csrf_exempt
def post_sensor_value(request):
    if AlsStatus.objects.count() > 100:
        first = AlsStatus.objects.first().id
        AlsStatus.objects.filter(id=first).delete()

    AlsStatus.objects.create(
        mac_address=request.POST.get("mac_address"),
        ip_address=request.POST.get("ip_address"),
        raw_value=request.POST.get("raw_value"),
        value= request.POST.get("value")
    )

    return redirect(f"knx/values/")
    

def render_sensor_values(request):
    status = AlsStatus.objects.all()

    context = {
        'status': status.values,
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'values',
    }

    return render(request, "knx/als_values.html", context)

def dect_ule(request):
    CMD_ROOT = "/usr/local/opend/openD/dspg/base/ule-hub/"
    INTERPRETER = "python3"
    command = request.GET.get("cmd")

    if command:
        process = subprocess.call(f"{INTERPRETER} { CMD_ROOT }{command}", shell=True)

    context = {
        'command': f"{INTERPRETER} { CMD_ROOT }{command}",
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'DECT ULE',
    }

    return render(request, "knx/dect_ule.html", context)
