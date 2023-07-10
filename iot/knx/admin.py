from django.contrib import admin

from knx.models import (
    Groupaddress,
    FunctionKeyLEDBoolRelation,
    AmbientLightRelation,
    TemperatureRelation,
)

admin.site.register(AmbientLightRelation)
admin.site.register(TemperatureRelation)


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


@admin.register(FunctionKeyLEDBoolRelation)
class FunctionKeyLEDBoolRelationAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Phone",
            {
                "fields": (
                    "phone_location",
                    ("phone_model", "mac_address", "ip_address"),
                )
            },
        ),
        (
            "Subscription",
            {
                "fields": (
                    ("write_groupaddress", "status_groupaddress"),
                    ("led_number", "led_color_for_on", "led_color_for_off"),
                    "led_number_mapping",
                )
            },
        ),
        (
            "Function keys action URLs",
            {"fields": (("knx_toggle_url"),)},
        ),
        (
            "Snom XML",
            {
                "fields": (
                    ("on_change_xml_for_on_url", "on_change_xml_for_off_url"),
                    ("on_change_xml_for_on", "on_change_xml_for_off"),
                )
            },
        ),
    )
    readonly_fields = [
        "led_number_mapping",
        "knx_toggle_url",
        "on_change_xml_for_on_url",
        "on_change_xml_for_off_url",
        "on_change_xml_for_on",
        "on_change_xml_for_off",
        "timestamp",
    ]
    search_fields = [
        "ip_address",
        "mac_address",
        "write_groupaddress",
        "status_groupaddress",
        "phone_model",
        "phone_location",
    ]
