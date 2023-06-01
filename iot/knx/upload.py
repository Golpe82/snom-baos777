import os

from django.core.files.storage import FileSystemStorage

from knx.groupaddresses import update_groupaddresses
from django.conf import settings


def process_file(request):
    if request.method != "POST":
        return ""

    uploaded_type = request.POST.get("file_type")

    if uploaded_type == ".csv":
        file = request.FILES.get("groupaddresses", False)
        post_request = HandleUploads(file)

        return post_request.handle_file(uploaded_type)

    return "Choose first a .csv file"


class HandleUploads:
    def __init__(self, file):
        self.file = file
        self.file_system = FileSystemStorage()

    def handle_file(self, file_type):
        TARGET_NAME = {".csv": "ga"}
        file_name = TARGET_NAME.get(".csv")
        file = f"{file_name}{file_type}"

        if self.file and file_type in self.file.name:
            self.file.name = file
            self.remove_file_if_exists()
            self.file_system.save(self.file.name, self.file)

            if file_type == ".csv":
                update_groupaddresses()

                return "Groupaddresses were uploaded."

            return f"Wrong file type {file_type}"

        return f"Choose first a {file_type }file"

    def remove_file_if_exists(self, file=None):
        if file:
            self.file.name = file

        if self.file_system.exists(self.file.name):
            os.remove(os.path.join(settings.MEDIA_ROOT, self.file.name))
