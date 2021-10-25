"""Snom sensors app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from snom_sensors import views


app_name = 'snom_sensors'

urlpatterns = [
    path('', views.home, name='snom_sensors_home'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)