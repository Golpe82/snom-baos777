import csv

from django.conf import settings

def get_groupaddresses_data():
    groupaddresses = []

    with open(settings.CSV_SOURCE_PATH, newline='', encoding='latin1') as csvfile:
        groupaddressesreader = csv.reader(csvfile)
        groupaddresses = list(groupaddressesreader)

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

    return {'header': header, 'groupaddresses': addresses}
