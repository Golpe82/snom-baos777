
from django.contrib import admin
from django.urls import path, include
from django.views.generic import TemplateView

from knx import urls as knx_urls
from dect import urls as dect_urls
from beacons import urls as beacons_urls
from snom_sensors import urls as snom_sensors_urls


urlpatterns = [
    path("", TemplateView.as_view(template_name="base_generic.html")),
    path("dect/", include(dect_urls, namespace="dect")),
    path("knx/", include(knx_urls, namespace="knx")),
    path("beacons/", include(beacons_urls, namespace="beacons")),
    path("snom_sensors/", include(snom_sensors_urls, namespace="snom_sensors")),
    path("admin/", admin.site.urls),
]
