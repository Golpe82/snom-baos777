import os
import logging

from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from knx.constants import FkeyLEDNo


class KnxMonitor(models.Model):
    groupaddress_name = models.CharField(max_length=50)
    groupaddress = models.CharField(max_length=9)
    datapoint_type = models.CharField(max_length=15)
    status = models.CharField(max_length=9)
    raw_frame = models.CharField(max_length=16384, default=0)
    timestamp = models.DateTimeField(auto_now_add=True)


class KnxStatus(models.Model):
    groupaddress_name = models.CharField(max_length=50)
    groupaddress = models.CharField(max_length=9)
    status = models.CharField(max_length=9)
    timestamp = models.DateTimeField(auto_now_add=True)


class AlsStatus(models.Model):
    device_name = models.CharField(max_length=4, default="D735")
    mac_address = models.CharField(max_length=12)
    ip_address = models.CharField(max_length=15)
    raw_value = models.IntegerField()
    value = models.FloatField()
    time_stamp = models.DateTimeField(null=True, auto_now_add=True)


class BrightnessRules(models.Model):
    device_name = models.CharField(max_length=4, default="D735")
    mac_address = models.CharField(max_length=12)
    ip_address = models.CharField(max_length=15)
    min_value = models.IntegerField()
    max_value = models.IntegerField()


class Device(models.Model):
    mac_address_validator = RegexValidator(
        regex="^[0-9a-fA-F]{12}$", message="Invalid MAC address"
    )
    mac_address = models.CharField(
        verbose_name="MAC address",
        max_length=12,
        validators=[mac_address_validator],
        unique=True,
        editable=False,
    )
    ip_address = models.GenericIPAddressField()
    manufacturers = [("Snom", "Snom")]
    manufacturer = models.CharField(
        max_length=20, choices=manufacturers, default="Snom"
    )
    types = [("D735", "D735")]
    type = models.CharField(max_length=4, choices=types, default="D735")
    label = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)


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
        return f"http://{settings.GATEWAY_IP}:8000/knx/write/{self.knx_subscription}/on"

    @property
    def knx_write_url_for_off(self):
        return f"http://{settings.GATEWAY_IP}:8000/knx/write/{self.knx_subscription}/off"

    @property
    def on_change_xml_for_on(self):
        subscriptions_path = f"/var/www/html/knx_led_subscriptions/{self.mac_address}/"

        if not os.path.exists(subscriptions_path):
            os.makedirs(subscriptions_path)
            logging.warning(f"Directory {subscriptions_path} created")

        file_name = f"{self.knx_subscription.replace('/', '_')}_on.xml"
        led_subscription_file_path = f"{subscriptions_path}{file_name}"

        if os.path.exists(led_subscription_file_path):
            os.remove(led_subscription_file_path)
            logging.warning(f"Existing file {led_subscription_file_path} deleted")

        content = f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <SnomIPPhoneText>
                <Text>Groupaddress {self.knx_subscription} changed to on</Text>
                <LED number="{self.led_number_for_on}" color="green">On</LED>
                <LED number="{self.led_number_for_off}">Off</LED>
                <fetch mil=1500>snom://mb_exit</fetch>
            </SnomIPPhoneText>
        """

        with open(led_subscription_file_path, 'w', encoding="UTF-8") as subscription_for_on:
            subscription_for_on.write(content)

        return content

    @property
    def on_change_xml_for_on_url(self):
        file_name = f"{self.knx_subscription.replace('/', '_')}_on.xml"

        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx_led_subscriptions/{self.mac_address}/{file_name}"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx_led_subscriptions/{self.mac_address}/{file_name}"

    @property
    def on_change_xml_for_off(self):
        subscriptions_path = f"/var/www/html/knx_led_subscriptions/{self.mac_address}/"

        if not os.path.exists(subscriptions_path):
            os.makedirs(subscriptions_path)
            logging.warning(f"Directory {subscriptions_path} created")

        file_name = f"{self.knx_subscription.replace('/', '_')}_off.xml"
        led_subscription_file_path = f"{subscriptions_path}{file_name}"

        if os.path.exists(led_subscription_file_path):
            os.remove(led_subscription_file_path)
            logging.warning(f"Existing file {led_subscription_file_path} deleted")

        content =  f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <SnomIPPhoneText>
            <Text>Groupaddress {self.knx_subscription} changed to off</Text>
            <LED number="{self.led_number_for_on}">Off</LED>
            <LED number="{self.led_number_for_off}" color="green">On</LED>
            <fetch mil=1500>snom://mb_exit</fetch>
        </SnomIPPhoneText>
        """

        with open(led_subscription_file_path, 'w', encoding="UTF-8") as subscription_for_off:
            subscription_for_off.write(content)

        return content

    @property
    def on_change_xml_for_off_url(self):
        file_name = f"{self.knx_subscription.replace('/', '_')}_off.xml"

        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx_led_subscriptions/{self.mac_address}/{file_name}"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.GATEWAY_IP}/knx_led_subscriptions/{self.mac_address}/{file_name}"

    def __str__(self) -> str:
        return f"Groupaddress: {self.knx_subscription} | {self.phone_model}: {self.ip_address} | LED on: {self.led_number_for_on} | LED off: {self.led_number_for_off}"

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
    phone_location = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

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
