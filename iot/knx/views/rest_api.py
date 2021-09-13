import requests
import logging

from django.http import JsonResponse

from knx.models import KnxStatus


GET_STATUS_URL_ROOT = "http://localhost:8000/knx/status/"

logging.basicConfig(level=logging.DEBUG)

def get_status(request_groupaddress):
    status = requests.get(f"{ GET_STATUS_URL_ROOT }{ request_groupaddress }/")

    return status

def get_groupaddress_status(request, main, midd, sub):
    request_address = f"{ main }/{ midd }/{ sub }"
    status_object = KnxStatus.objects.get(groupaddress=request_address)

    logging.info(f"Status of { status_object.groupaddress }: { status_object.status }")

    data = {
        "Groupaddress": status_object.groupaddress,
        "Status": status_object.status
    }

    return JsonResponse(data)