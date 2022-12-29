import requests
import logging
from datetime import datetime

from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse

from knx.models import KnxStatus, AlsStatus, KnxMonitor


POST_RESPONSE = {"POST": "OK"}
logging.basicConfig(level=logging.DEBUG)


def get_groupaddress_status(request, main, midd, sub):
    request_address = f"{ main }/{ midd }/{ sub }"
    status_object = KnxStatus.objects.filter(groupaddress=request_address).latest("status")

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

    return JsonResponse(POST_RESPONSE)

@csrf_exempt
def post_knx_status(request):
    status_object, _created = KnxStatus.objects.update_or_create(
        groupaddress_name=request.POST.get("groupaddress_name"),
        groupaddress=request.POST.get("groupaddress"),
        defaults={
            "status": request.POST.get("status"),
            "timestamp": datetime.now()
        }
    )
    logging.info(f"{ status_object.groupaddress_name }: { status_object.status }")

    return JsonResponse(POST_RESPONSE)

@csrf_exempt
def post_knx_monitor(request):
    if KnxMonitor.objects.count() > 2000:
        first = KnxMonitor.objects.first().id
        KnxMonitor.objects.filter(id=first).delete()
    logging.info(request.POST.get("raw_frame"))

    KnxMonitor.objects.create(
        groupaddress_name=request.POST.get("groupaddress_name"),
        groupaddress=request.POST.get("groupaddress"),
        datapoint_type=request.POST.get("datapoint_type"),
        status=request.POST.get("status"),
        raw_frame=request.POST.get("raw_frame")
    )

    return JsonResponse(POST_RESPONSE)
