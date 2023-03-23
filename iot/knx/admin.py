from django.contrib import admin

from knx.models import AlsStatus, Device, Groupaddress, FunctionKeyLEDSubscriptions

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

@admin.register(FunctionKeyLEDSubscriptions)
class FunctionKeyLEDSubscriptionsAdmin(admin.ModelAdmin):
    readonly_fields = [
        "led_number_mapping",
        "knx_write_url_for_on",
        "knx_write_url_for_off",
        "on_change_xml_for_on_url",
        "on_change_xml_for_off_url",
        "on_change_xml_for_on",
        "on_change_xml_for_off",
        "timestamp",
    ]
