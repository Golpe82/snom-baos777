"""Views for app knx"""
import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse

from knx import groupaddresses, upload

APP = 'KNX'

def index(request):
    if os.path.exists(settings.CSV_SOURCE_PATH):
        groupaddresses_data = groupaddresses.get_groupaddresses_data()

        context = {
            'project': settings.PROJECT_NAME,
            'app': APP,
            'page': 'Groupaddresses',
            'header': groupaddresses_data['header'],
            'groupaddresses': groupaddresses_data['groupaddresses'],
            'knx_gateway': settings.KNX_ROOT,
            }

        return render(request, 'knx/groupaddresses.html', context)

    prompt = '<h1><a href="upload/">Upload</a> first your .csv file with the KNX addresses</h1>'

    return HttpResponse(prompt)

def minibrowser(request):
    return render(request, 'knx/minibrowser.xml', content_type="application/xhtml+xml")

def upload_file(request):

    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Upload',
        'message': upload.process_file(request),
    }

    return render(request, 'knx/upload.html', context)
