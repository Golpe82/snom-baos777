"""Beacons app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from beacons import views


app_name = 'beacons'

urlpatterns = [
    path('', views.home, name='beacons_home'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)