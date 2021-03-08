"""Views for app knx"""
import os

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
