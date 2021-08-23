"""Views for app knx"""
import os
import csv
import subprocess
import requests
import logging

from django.conf import settings
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from knx import groupaddresses, upload
from knx.models import AlsStatus, BrightnessRules, KnxMonitor

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

    return redirect("knx/values/") 

def render_sensor_values(request):
    if BrightnessRules.objects.filter(mac_address="000413A34795"):
        BrightnessRules.objects.filter(mac_address="000413A34795").delete()

    BrightnessRules.objects.create(
        mac_address="000413A34795",
        ip_address="192.168.178.66",
        min_value="100",
        max_value="110"
    )

    status = AlsStatus.objects.all()
    rules = BrightnessRules.objects.all()

    context = {
        'status': status.values,
        'rules': rules.values,
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'values',
    }

    return render(request, "knx/als_values.html", context)

def get_rules(request):
    rules = BrightnessRules.objects.filter(mac_address="000413A34795").values("min_value", "max_value")
    print(rules)

    return HttpResponse(rules)

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

@csrf_exempt
def post_knx_monitor(request):
    if KnxMonitor.objects.count() > 2000:
        first = KnxMonitor.objects.first().id
        KnxMonitor.objects.filter(id=first).delete()

    KnxMonitor.objects.create(
        groupaddress_name=request.POST.get("groupaddress_name"),
        groupaddress=request.POST.get("groupaddress"),
        datapoint_type=request.POST.get("datapoint_type"),
        status=request.POST.get("status")
    )

    return redirect("knx/monitor/")

def knx_monitor(request):
    monitor = KnxMonitor.objects.all()

    context = {
        "monitor": monitor.values,
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'MONITOR',
    }

    return render(request, "knx/knx_monitor.html", context)

def knx_status(request):
    monitor = KnxMonitor.objects.all()
    ga_qset = monitor.values_list("groupaddress_name").distinct()
    ga_list = []
    for ga in ga_qset:
        for a in ga:
            ga_list.append(a)

    status = [
        monitor.filter(groupaddress_name=groupaddress).last()
        for groupaddress in ga_list
    ]

    context = {
        "status": status,
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'MONITOR',
    }

    return render(request, "knx/knx_status.html", context)
