import requests
import logging

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from knx.models import KnxStatus, AlsStatus


logging.basicConfig(level=logging.DEBUG)


def get_groupaddress_status(request, main, midd, sub):
    request_address = f"{ main }/{ midd }/{ sub }"
    status_object = KnxStatus.objects.get(groupaddress=request_address)

    logging.info(f"Status of { status_object.groupaddress }: { status_object.status }")

    data = {
        "Groupaddress": status_object.groupaddress,
        "Status": status_object.status
    }

    return JsonResponse(data)

@csrf_exempt
def post_sensor_value(request):
    if AlsStatus.objects.count() > 100:
        first = AlsStatus.objects.first().id
        AlsStatus.objects.filter(id=first).delete()

    AlsStatus.objects.create(
        mac_address=request.POST.get("mac_address"),
        ip_address=request.POST.get("ip_address"),
        raw_value=request.POST.get("raw_value"),
        value= request.POST.get("value")
    )
