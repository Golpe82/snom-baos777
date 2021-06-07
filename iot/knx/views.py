"""Views for app knx"""
import os
import csv

from django.conf import settings
from django.shortcuts import render

from knx import groupaddresses, upload

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

def ambientlight_sensors(request):
    AMBIENTLIGHT_STATUS_FILE = "/usr/local/gateway/snomsyslogknx/AlsStatus.csv"
    # TODO: Use AJAX for rendering the als value
    # TODO: Use function of snomsyslogknx instead of this

    with open(AMBIENTLIGHT_STATUS_FILE) as als_status:
        fieldnames = ["Phone MAC", "Phone IP", "ALS row value", "ALS value (Lux)"]
        reader = csv.DictReader(als_status)
        for phone in reader:
            values = dict((field, phone[field]) for field in fieldnames)

        context = {
            'project': settings.PROJECT_NAME,
            "als_value": values,
            'app': APP,
            'page': 'Ambientlight sensors',
        }

    return render(request, "knx/ambientlight.html", context)
