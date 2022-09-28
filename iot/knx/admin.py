from django.contrib import admin

from knx.models import AlsStatus, Device

admin.site.register(AlsStatus)
admin.site.register(Device)
