from django.core.validators import RegexValidator
from django.db import models


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
        editable=False
    )
    ip_address = models.GenericIPAddressField()
    manufacturers = [("Snom", "Snom")]
    manufacturer = models.CharField(max_length=20, choices=manufacturers, default="Snom")
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
