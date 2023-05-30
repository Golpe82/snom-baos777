import os
import logging

from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from knx.constants import FkeyLEDNo


class Groupaddress(models.Model):
    maingroup = models.CharField(max_length=50, default=None, editable=False)
    subgroup = models.CharField(max_length=50, default=None, editable=False)
    address = models.CharField(max_length=9, default=None, editable=False)
    name = models.CharField(max_length=50, default=None, editable=False)
    alias = models.CharField(max_length=50, default=None)
    datapoint_type = models.CharField(max_length=50, default=None, editable=False)
    html_action = models.CharField(max_length=500, default=None)
    code = models.CharField(max_length=4, blank=True)

    def __str__(self) -> str:
        return f"{self.maingroup} | {self.subgroup} | {self.name}"

PHONE_MODEL_CHOICES = [(phone_model, phone_model) for phone_model in FkeyLEDNo.__dataclass_fields__]

class FunctionKeyLEDSubscriptions(models.Model):
    mac_address_validator = RegexValidator(
        regex="^[0-9a-fA-F]{12}$", message="Invalid MAC address"
    )
    mac_address = models.CharField(
        verbose_name="MAC address",
        max_length=12,
        validators=[mac_address_validator],
    )
    ip_address = models.GenericIPAddressField()
    phone_model = models.CharField(max_length=4, null=True, choices=PHONE_MODEL_CHOICES)
    led_number_for_on = models.PositiveSmallIntegerField(null=True)
    led_number_for_off = models.PositiveSmallIntegerField(default=None)
    knx_subscription = models.CharField(max_length=8, null=True)
    phone_location = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    @property
    def led_number_mapping(self):
        return {
            phone_model.name: [*phone_model.default]
            for phone_model in FkeyLEDNo.__dataclass_fields__.values()
        }

    @property
    def knx_write_url_for_on(self):
        return f"{settings.KNX_ROOT}write/{self.knx_subscription}/switch/on"

    @property
    def knx_write_url_for_off(self):
        return f"{settings.KNX_ROOT}write/{self.knx_subscription}/switch/off"

    @property
    def on_change_xml_for_on(self):
        return f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <SnomIPPhoneText>
                <Title>LED subscription</Title>
                <Text>Groupaddress {self.knx_subscription} changed to on</Text>
                <LED number="{self.led_number_for_on}" color="green">On</LED>
                <LED number="{self.led_number_for_off}">Off</LED>
                <fetch mil=1>snom://mb_exit</fetch>
            </SnomIPPhoneText>
        """

    @property
    def on_change_xml_for_on_url(self):
        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx/minibrowser/subscription/{self.id}/on/"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx/minibrowser/subscription/{self.id}/on/"

    @property
    def on_change_xml_for_off(self):
        return  f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <SnomIPPhoneText>
            <Title>LED subscription</Title>
            <Text>Groupaddress {self.knx_subscription} changed to off</Text>
            <LED number="{self.led_number_for_on}">Off</LED>
            <LED number="{self.led_number_for_off}" color="green">On</LED>
            <fetch mil=1>snom://mb_exit</fetch>
        </SnomIPPhoneText>
        """

    @property
    def on_change_xml_for_off_url(self):
        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx/minibrowser/subscription/{self.id}/off/"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx/minibrowser/subscription/{self.id}/off/"

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Switch groupaddress: {self.knx_subscription}"

class AmbientLightRelation(models.Model):
    mac_address_validator = RegexValidator(
        regex="^[0-9a-fA-F]{12}$", message="Invalid MAC address"
    )
    mac_address = models.CharField(
        verbose_name="MAC address",
        max_length=12,
        validators=[mac_address_validator],
    )
    ip_address = models.GenericIPAddressField()
    phone_model = models.CharField(max_length=4, null=True, choices=[("D735", "D735")])
    knx_send_lux_address = models.CharField(max_length=8, null=True)
    lux_delta = models.FloatField(default=10)
    knx_switch_address = models.CharField(max_length=8, null=True)
    min_lux = models.PositiveSmallIntegerField(default=100)
    max_lux = models.PositiveSmallIntegerField(default=500)
    knx_dimm_address = models.CharField(max_length=8, null=True)
    knx_dimm_status_address = models.CharField(max_length=8, null=True)
    phone_location = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Lux groupaddress: {self.knx_send_lux_address} | Setpoint: {self.min_lux}...{self.max_lux} Lux"

class TemperatureRelation(models.Model):
    mac_address_validator = RegexValidator(
        regex="^[0-9a-fA-F]{12}$", message="Invalid MAC address"
    )
    mac_address = models.CharField(
        verbose_name="MAC address",
        max_length=12,
        validators=[mac_address_validator],
    )
    ip_address = models.GenericIPAddressField()
    phone_model = models.CharField(max_length=4, null=True, choices=PHONE_MODEL_CHOICES)
    knx_send_celsius_address = models.CharField(max_length=8, null=True)
    celsius_delta = models.FloatField(default=1)
    phone_location = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Celsius groupaddress: {self.knx_send_celsius_address}"
