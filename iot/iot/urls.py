
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic import TemplateView

from knx import urls as knx_urls


urlpatterns = [
    path("", TemplateView.as_view(template_name="base_generic.html")),
    path("knx/", include(knx_urls, namespace="knx")),
    path("admin/", admin.site.urls),
]

urlpatterns += staticfiles_urlpatterns()
