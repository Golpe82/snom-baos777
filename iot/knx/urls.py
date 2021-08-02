"""knx app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from knx import views


app_name = 'knx'

urlpatterns = [
    path('', views.index, name='start'),
    path('minibrowser/', views.minibrowser, name='minibrowser'),
    path('upload/', views.upload_file, name='upload_file'),
    path('ambientlight/', views.ambientlight_sensors, name='ambientlight'),
    path('values/', views.render_sensor_values, name='render_values'),
    path('values', views.post_sensor_value, name='post_values'),
    path('dect-ule/', views.dect_ule, name='dect_ule'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    