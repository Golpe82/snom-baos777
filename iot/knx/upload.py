import os
import csv

from django.core.files.storage import FileSystemStorage

from knx.xml import SnomXMLFactory
from knx.models import Groupaddress
from django.conf import settings

SOURCE_FILE = settings.CSV_SOURCE_PATH
CSV_FIELDS = {
    'Group name': 0, 'Address': 1, 'Central': 2, 'Unfiltered': 3,
    'Description': 4, 'DatapointType': 5, 'Security': 6,
}


def process_file(request):
    TARGET_NAME = {'.csv': 'ga', '.xml': 'knx'}

    if request.method == 'POST':
        uploaded_type = request.POST.get('file_type')

        if uploaded_type == '.csv':
            file = request.FILES.get('groupaddresses', False)
            post_request = HandleUploads(file)

            return post_request.handle_file(TARGET_NAME.get('.csv'), uploaded_type)

        if uploaded_type == '.xml':
            file = request.FILES.get('minibrowser', False)
            post_request = HandleUploads(file)

            return post_request.handle_file(TARGET_NAME['.xml'], uploaded_type)

        return 'Choose first a file'

    return ''


class HandleUploads:
    def __init__(self, file):
        self.file = file
        self.file_system = FileSystemStorage()

    def handle_file(self, file_name, file_type):
        file = f"{ file_name }{ file_type }"

        if self.file and file_type in self.file.name:
            self.file.name = file
            self.remove_file_if_exists()
            self.file_system.save(self.file.name, self.file)

            if file_type == '.csv':
                self._update_xml(file)
                self._update_groupaddresses()

                return 'Groupaddresses were uploaded and Snom default XML was created.'

            return 'Snom XML was updated'

        return f'Choose first a { file_type } file'

    def _update_xml(self, file):
        self.remove_file_if_exists('minibrowser.xml')
        xml_object = SnomXMLFactory(file)
        xml_object.create_multi_xml()
        xml_object.create_single_xml()

    def remove_file_if_exists(self, file=None):
        if file:
            self.file.name = file

        if self.file_system.exists(self.file.name):
            os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))

    def _update_groupaddresses(self):
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
                    # data[maingroup][subgroup][groupaddress_name] = {
                    #     "groupaddress": row["Address"],
                    #     "datapoint_type": row['DatapointType'],
                    #     #"dom": get_dom_action(row['DatapointType'], row["Address"], groupaddress_name)
                    # }
                    Groupaddress.objects.create(
                        maingroup=maingroup,
                        subgroup=subgroup,
                        address=groupaddress,
                        name=groupaddress_name,
                        alias=groupaddress_name,
                        datapoint_type=datapoint_type,
                        html_action=self.get_dom_action(datapoint_type, groupaddress, groupaddress_name)
                    )


    def get_dom_action(self, datapoint_type, groupaddress, groupaddress_name):
        is_dpt1 = 'DPT-1' in datapoint_type or 'DPST-1-' in datapoint_type
        is_dpt3 = 'DPT-3' in datapoint_type or 'DPST-3-' in datapoint_type
        is_status = "DPST-1-11" in datapoint_type

        if is_status:
            return "<div>Fetch status not implemented</div>"

        elif is_dpt1:
            on = f"<button id='{groupaddress}_on' formaction='{settings.KNX_ROOT}{groupaddress}-an' type='submit' name='{groupaddress_name}' value='on'>On</button>\n"
            off = f"<button id='{groupaddress}_off' formaction='{settings.KNX_ROOT}{groupaddress}-aus' type='submit' name='{groupaddress_name}' value='off'>Off</button>\n"

            return ("<form method='get'>"
                    f"{on}"
                    f"{off}"
                "</form>")

        elif is_dpt3:
            plus = f"<button id='{groupaddress}_plus' formaction='{settings.KNX_ROOT}{groupaddress}-plus' type='submit' name='{groupaddress_name}' value='plus'>+</button>\n"
            minus = f"<button id='{groupaddress}_minus' formaction='{settings.KNX_ROOT}{groupaddress}-minus' type='submit' name='{groupaddress_name}' value='minus'>-</button>\n"

            return ("<form method='get'>"
                    f"{plus}"
                    f"{minus}"
                "</form>")

        else:
            return "<div>Datapoint type or subtype not implemented</div>"

