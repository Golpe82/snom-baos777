"""knx app URLs configuration"""
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static

from knx import views


app_name = 'knx'

urlpatterns = [
    path('', views.index, name='knx_home'),
    path("update_led_subscriptors/<int:main>/<int:midd>/<int:sub>/<str:status>", views.update_led_subscriptors, name="update_led_subscriptors"),
    re_path(
        r"^write/([0-9]+)/([0-9]+)/([0-9]+)/(on|off|increase|decrease)/(.*)$", views.check_code, name="check_code"
    ),
    re_path(
        r"^write/([0-9]+)/([0-9]+)/([0-9]+)/(on|off|increase|decrease)$", views.knx_write, name="knx_write"
    ),
    path('addresses/<str:maingroup>/<str:subgroup>/', views.addresses, name='addresses'),
    path('minibrowser/', views.minibrowser, name='minibrowser'),
    path('upload/', views.upload_file, name='upload_file'),
    path('values/', views.render_sensor_values, name='render_values'),
    path('groupaddresses/', views.render_groupaddresses, name='groupaddresses'),
    path('rules/', views.get_rules, name='get_rules'),
    path('dect-ule/', views.dect_ule, name='dect_ule'),
    path('monitor/', views.knx_monitor, name='knx_monitor'),
    path('status/', views.knx_status, name='knx_status'),
    # REST API URLs
    path('values', views.post_sensor_value, name='post_values'),
    path('status', views.post_knx_status, name='post_knx_status'),
    path('groupaddress_monitor', views.post_knx_monitor, name='post_knx_monitor'),
    path('status/<int:main>/<int:midd>/<int:sub>/', views.get_groupaddress_status, name='get_groupaddress_status'),
    path('read/<int:main>/<int:midd>/<int:sub>/', views.knx_read, name="knx_read"),
]

# serve during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    