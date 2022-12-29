from django.contrib import admin

from knx.models import AlsStatus, Device, Groupaddress

admin.site.register(AlsStatus)
admin.site.register(Device)


@admin.register(Groupaddress)
class GroupaddressAdmin(admin.ModelAdmin):
    readonly_fields = [
        "maingroup",
        "subgroup",
        "address",
        "name",
        "datapoint_type",
        "html_action",
    ]
