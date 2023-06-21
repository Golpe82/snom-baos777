import logging

from django.core.validators import RegexValidator
from django.db import models
from django.conf import settings
from knx.constants import FkeyLEDNo

class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        pass

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

class Setting(SingletonModel):
    baos777_ip_address = models.GenericIPAddressField()
    
    @property
    def local_ip_address(self):
        return settings.LOCAL_IP

    def __str__(self) -> str:
        return f"Settings | BAOS IP {self.baos777_ip_address}"

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

PHONE_MODEL_CHOICES = [
    (phone_model, phone_model) for phone_model in FkeyLEDNo.__dataclass_fields__
]
LED_COLOR_CHOICES = [
    ("---", "---"),
    ("green", "green"),
    ("red", "red"),
    ("orange", "orange"),
]

class FunctionKeyLEDBoolRelation(models.Model):
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
    write_groupaddress = models.CharField(max_length=8, null=True)
    status_groupaddress = models.CharField(max_length=8, null=True)
    led_number = models.PositiveSmallIntegerField(null=True)
    led_color_for_on = models.CharField(max_length=8, null=True, choices=LED_COLOR_CHOICES)
    led_color_for_off = models.CharField(max_length=8, null=True, choices=LED_COLOR_CHOICES, default="---")
    phone_location = models.CharField(max_length=30, default=None)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    @property
    def led_number_mapping(self):
        return {
            phone_model.name: [*phone_model.default]
            for phone_model in FkeyLEDNo.__dataclass_fields__.values()
        }

    @property
    def knx_toggle_url(self):
        return f"{settings.KNX_ROOT}write/{self.write_groupaddress}/switch/toggle"

    @property
    def on_change_xml_for_on(self):
        return f"""
            <?xml version="1.0" encoding="UTF-8"?>
            <SnomIPPhoneText>
                <Title>LED subscription</Title>
                <Text>Groupaddress {self.status_groupaddress} changed to on</Text>
                <LED number="{self.led_number}" color="{self.led_color_for_on}">On</LED>
                <fetch mil=1>snom://mb_exit</fetch>
            </SnomIPPhoneText>
        """

    @property
    def on_change_xml_for_on_url(self):
        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.LOCAL_IP}/knx/minibrowser/subscription/{self.id}/on/"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.LOCAL_IP}/knx/minibrowser/subscription/{self.id}/on/"

    @property
    def on_change_xml_for_off(self):
        if self.led_color_for_off == "---":
            led_tag = f"<LED number='{self.led_number}'>Off</LED>"
        else:
            led_tag = f"<LED number='{self.led_number}' color='{self.led_color_for_off}'>On</LED>"

        return f"""
        <?xml version="1.0" encoding="UTF-8"?>
        <SnomIPPhoneText>
            <Title>LED subscription</Title>
            <Text>Groupaddress {self.status_groupaddress} changed to off</Text>
            {led_tag}
            <fetch mil=1>snom://mb_exit</fetch>
        </SnomIPPhoneText>
        """

    @property
    def on_change_xml_for_off_url(self):
        if self.phone_model.startswith("D8"):
            return f"http://{self.ip_address}:3112/minibrowser.htm?url=http://{settings.LOCAL_IP}/knx/minibrowser/subscription/{self.id}/off/"

        return f"http://{self.ip_address}/minibrowser.htm?url=http://{settings.LOCAL_IP}/knx/minibrowser/subscription/{self.id}/off/"

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Write groupaddress: {self.write_groupaddress}"

class AmbientLightRelation(models.Model):
    phone_location = models.CharField(max_length=30, default=None)
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
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Lux groupaddress: {self.knx_send_lux_address} | Setpoint: {self.min_lux}...{self.max_lux} Lux"

class TemperatureRelation(models.Model):
    phone_location = models.CharField(max_length=30, default=None)
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
    min_celsius = models.PositiveSmallIntegerField(default=16)
    max_celsius = models.PositiveSmallIntegerField(default=28)
    action_groupaddress = models.CharField(max_length=8, null=True)
    timestamp = models.DateTimeField(null=True, auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.phone_location} | {self.phone_model}: {self.ip_address} | Celsius groupaddress: {self.knx_send_celsius_address}"

class Subprocess(models.Model):
    pid = models.PositiveIntegerField(default=None, unique=True)
    type = models.CharField(max_length=10, default=None, editable=False)
    name = models.CharField(max_length=50, default=None, editable=False)

    def __str__(self) -> str:
        return f"{self.type} | {self.name} | {self.pid}"
