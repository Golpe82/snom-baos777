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
    fieldsets = (
        ("Phone",
            {
                "fields":(
                    "phone_location",
                    ("phone_model", "mac_address", "ip_address")
                )
            }
        ),
        ("Subscription",
            {
                "fields":(
                    ("knx_subscription", "led_number_for_on", "led_number_for_off"),
                    "led_number_mapping"
                )
            }
        ),
        ("Function keys action URLs",
            {
                "fields":(("knx_write_url_for_on", "knx_write_url_for_off"))
            }
        ),
        ("Snom XML",
            {
                "fields":(
                    ("on_change_xml_for_on_url", "on_change_xml_for_off_url"),
                    ("on_change_xml_for_on", "on_change_xml_for_off")
                )
            }
        ),
    )
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
    search_fields = ["ip_address", "mac_address", "knx_subscription", "phone_model", "phone_location"]
