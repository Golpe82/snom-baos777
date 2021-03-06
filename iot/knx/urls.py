"""knx app URLs configuration"""
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from knx import views


app_name = 'knx'

urlpatterns = [
    path('', views.index, name='start'),
    path('minibrowser/', views.minibrowser, name='minibrowser'),
    path('upload/', views.upload, name='upload'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    