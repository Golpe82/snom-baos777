"""knx app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from dect import views


app_name = 'dect'

urlpatterns = [
    path('', views.home, name='dect_home'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    