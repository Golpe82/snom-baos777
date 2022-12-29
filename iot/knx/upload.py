import os

from django.core.files.storage import FileSystemStorage

from knx.xml import SnomXMLFactory
from knx.groupaddresses import update_groupaddresses
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
                update_groupaddresses()

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
