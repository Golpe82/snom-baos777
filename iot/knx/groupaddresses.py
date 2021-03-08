import csv

from django.conf import settings

SOURCE_FILE = settings.CSV_SOURCE_PATH
CSV_FIELDS = {
    'Group name': 0, 'Address': 1, 'Central': 2, 'Unfiltered': 3,
    'Description': 4, 'DatapointType': 5, 'Security': 6,
}

def get_data():
    data = []

    with open(SOURCE_FILE, newline='', encoding='latin1') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=CSV_FIELDS.keys())

        for row in reader:
            if row['Group name'] == 'Group name':
                continue

            address_info = {
                'Groupname': row['Group name'],
                'Groupaddress': row['Address'],
                'Datapointtype': row['DatapointType'],
            }
            data.append(address_info)

    return {
        'header': data[0].keys(),
        'data': data,
    }
