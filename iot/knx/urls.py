"""knx app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from knx import views


app_name = 'knx'

urlpatterns = [
    path('', views.index, name='knx_home'),
    path('minibrowser/', views.minibrowser, name='minibrowser'),
    path('upload/', views.upload_file, name='upload_file'),
    path('values/', views.render_sensor_values, name='render_values'),
    path('rules/', views.get_rules, name='get_rules'),
    path('dect-ule/', views.dect_ule, name='dect_ule'),
    path('monitor/', views.knx_monitor, name='knx_monitor'),
    path('status/', views.knx_status, name='knx_status'),
    # REST API URLs
    path('values', views.post_sensor_value, name='post_values'),
    path('status', views.post_knx_status, name='post_knx_status'),
    path('groupaddress_monitor', views.post_knx_monitor, name='post_knx_monitor'),
    path('status/<int:main>/<int:midd>/<int:sub>/', views.get_groupaddress_status, name='get_groupaddress_status'),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    