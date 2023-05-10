import csv

from django.conf import settings

from knx.models import Groupaddress

SOURCE_FILE = settings.CSV_SOURCE_PATH
CSV_FIELDS = {
    "Group name": 0,
    "Address": 1,
    "Central": 2,
    "Unfiltered": 3,
    "Description": 4,
    "DatapointType": 5,
    "Security": 6,
}


def update_groupaddresses():
    Groupaddress.objects.all().delete()
    data = {}
    maingroup_id = "/-/-"
    subgroup_id = "/-"
    maingroup = ""
    subgroup = ""

    with open(SOURCE_FILE, newline='', encoding='latin1') as csv_file:
        reader = csv.DictReader(csv_file, fieldnames=CSV_FIELDS.keys())

        for row in reader:
            if row['Group name'] == 'Group name':
                continue
            elif maingroup_id in row["Address"]:
                maingroup = row['Group name']
                data[maingroup] = {}
            elif subgroup_id in row["Address"]:
                subgroup = row['Group name']
                data[maingroup][subgroup] = {}
            else: 
                groupaddress_name = row['Group name']
                groupaddress = row["Address"]
                datapoint_type = row['DatapointType']
                Groupaddress.objects.create(
                    maingroup=maingroup,
                    subgroup=subgroup,
                    address=groupaddress,
                    name=groupaddress_name,
                    alias=groupaddress_name,
                    datapoint_type=datapoint_type,
                    html_action=_get_dom_action(datapoint_type, groupaddress, groupaddress_name)
                )


def _get_dom_action(datapoint_type, groupaddress, groupaddress_name):
    is_dpt1 = 'DPT-1' in datapoint_type or 'DPST-1-' in datapoint_type
    is_dpt3 = 'DPT-3' in datapoint_type or 'DPST-3-' in datapoint_type

    if datapoint_type == "DPST-1-11":
        return "<div>Fetch status not implemented</div>"

    elif is_dpt1:
        on = f"<button id='{groupaddress}_on' formaction='{settings.KNX_ROOT}write/{groupaddress}/switch/on' type='submit' name='{groupaddress_name}' value='on'>On</button>\n"
        off = f"<button id='{groupaddress}_off' formaction='{settings.KNX_ROOT}write/{groupaddress}/switch/off' type='submit' name='{groupaddress_name}' value='off'>Off</button>\n"

        return ("<form method='get'>"
                f"{on}"
                f"{off}"
            "</form>")

    elif is_dpt3:
        plus = f"<button id='{groupaddress}_plus' formaction='{settings.KNX_ROOT}write/{groupaddress}/dimming/increase' type='submit' name='{groupaddress_name}' value='plus'>+</button>\n"
        minus = f"<button id='{groupaddress}_minus' formaction='{settings.KNX_ROOT}write/{groupaddress}/dimming/decrease' type='submit' name='{groupaddress_name}' value='minus'>-</button>\n"

        return ("<form method='get'>"
                f"{plus}"
                f"{minus}"
            "</form>")

    else:
        return "<div>Datapoint type or subtype not implemented</div>"
