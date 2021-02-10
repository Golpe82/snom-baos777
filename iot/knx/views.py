"""Views for app knx"""
import csv
import os

from django.conf import settings
from django.shortcuts import render
from django.http import HttpResponse
from django.core.files.storage import FileSystemStorage

APP = 'KNX'

def groupaddresses(request):
    source_path = settings.CSV_SOURCE_PATH
    target_path = settings.CSV_TARGET_PATH
    groupaddresses = []

    if os.path.exists(source_path):
        with open(target_path, newline='', encoding='latin1') as csvfile:
            groupaddressesreader = csv.reader(csvfile)
            groupaddresses = [groupaddress for groupaddress in groupaddressesreader]

        first_line = groupaddresses[0]

        if first_line[0] == 'Group name':
            header = first_line
            header[6:] = []
            header[2:5] = []
            addresses = groupaddresses[1:]

        else:
            header = ['Group name', 'Address', 'DatapointType']
            addresses = groupaddresses

        for line in addresses:
            line[6:] = []
            line[2:5] = []

        context = {
            'project': settings.PROJECT_NAME,
            'app': APP,
            'page': 'Groupaddresses',
            'header': header,
            'groupaddresses': addresses,
            'knx_gateway': settings.KNX_ROOT,
            }

        return render(request, 'knx/groupaddresses.html', context)

    else:
        return HttpResponse('<h1><a href="upload/">Upload</a> first your .csv file with the KNX addresses</h1>')

def minibrowser(request):
    return render(request, 'knx/minibrowser.xml', content_type="application/xhtml+xml")

def upload(request):
    context = {
        'project': settings.PROJECT_NAME,
        'app': APP,
        'page': 'Upload',
    }

    if request.method =='POST':

        if request.POST.get('csv') == '.csv':
            uploaded_file = request.FILES['groupaddresses']
            file_system = FileSystemStorage()

            if '.csv' in uploaded_file.name:
                uploaded_file.name = 'ga.csv'
                if file_system.exists(uploaded_file.name):
                    os.remove(os.path.join(settings.MEDIA_ROOT, uploaded_file.name))
                file_system.save(uploaded_file.name, uploaded_file)

                if file_system.exists('minibrowser.xml'):
                    os.remove(os.path.join(settings.MEDIA_ROOT, 'minibrowser.xml'))

                create_xml()

                context['message'] = 'Groupaddresses successfully uploaded.'

            else:
                context['message'] = 'upload please a .csv file'

        if request.POST.get('xml') == '.xml':
            uploaded_file = request.FILES['minibrowser']
            file_system = FileSystemStorage()

            if '.xml' in uploaded_file.name:
                uploaded_file.name = 'knx.xml'
                if file_system.exists(uploaded_file.name):
                    os.remove(os.path.join(settings.MEDIA_ROOT, uploaded_file.name))
                file_system.save(uploaded_file.name, uploaded_file)
                context['message'] = 'XML file successfully uploaded'

            else:
                context['message'] = 'upload please a .xml file'

    return render(request, 'knx/upload.html', context)

def create_xml():
    csv_file = 'ga.csv'
    xml_file = settings.XML_TARGET_PATH

    csv_data = csv.reader(open(f"{ settings.MEDIA_ROOT }{ csv_file }", encoding='latin-1'))
    data = [line for line in csv_data]
    xml_data = open(xml_file, 'w')
    xml_data.write(
    '''<?xml version="1.0"?>
    '''
    )
    # there must be only one top-level tag
    xml_data.write(
"""
<SnomIPPhoneMenu document_id="control">
    <Title>KNX Snom</Title>"""
    )

    tag1 = ''
    tag2 = ''

    for row in data:
        if '/-/-' in row[1]:
            if tag2 == 'open':
                xml_data.write(
        """
        </Menu>"""
                )
                tag2 = ''

            if tag1 == 'open':
                xml_data.write(
    """
    </Menu>"""
                )
                tag1 = ''   

            xml_data.write(
    f"""
    <Menu Name='{ row[0] }'>
    <Name>{ row[0] }</Name>"""
                )
            tag1 = 'open'
            continue

        elif '/-' in row[1]:
            if tag2 == 'open':
                xml_data.write(
        """
        </Menu>"""
                )
            tag2 = ''

            xml_data.write(
        f"""
        <Menu Name='{ row[0] }'>
        <Name>{ row[0] }</Name>"""
            )
            tag2 = 'open'
            continue

        elif 'DPST-1-' in row[5] and 'DPST-1-11' not in row[5]:
            xml_data.write(
            f"""
            <Menu Name='{ row[0] }'>
            <Name>{ row[0] }</Name>
                <MenuItem>
                <Name>on</Name>
                    <URL>{ settings.KNX_ROOT }{ row[1] }-an</URL>
                </MenuItem>
                <MenuItem>
                <Name>off</Name>
                    <URL>{ settings.KNX_ROOT }{ row[1] }-aus</URL>
                </MenuItem>
            </Menu>"""
            )
            continue
        elif 'DPST-3-' in row[5]:
            xml_data.write(
            f"""
            <Menu Name='{ row[0] }'>
            <Name>{ row[0] }</Name>
                <MenuItem>
                <Name>plus</Name>
                    <URL>{ settings.KNX_ROOT }{ row[1] }-plus</URL>
                </MenuItem>
                <MenuItem>
                <Name>minus</Name>
                    <URL>{ settings.KNX_ROOT }{ row[1] }-minus</URL>
                </MenuItem>
            </Menu>"""
            )
            continue

        elif '-' not in row[1]:
            continue

        if tag1 == 'open':
                xml_data.write(
        """
        </Menu>"""
                )
                tag1 = ''

    if tag2 == 'open':
            xml_data.write(
        """
        </Menu>"""
            )
            tag2 = ''
    if tag1 == 'open':

        xml_data.write(
    """
    </Menu>"""
        )

    xml_data.write(
    """
</SnomIPPhoneMenu>"""
    )
    xml_data.close()

    return xml_data
