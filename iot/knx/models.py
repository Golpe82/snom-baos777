from django.db import models


class KnxMonitor(models.Model):
    groupaddress_name = models.CharField(max_length=50)
    groupaddress = models.CharField(max_length=9)
    datapoint_type = models.CharField(max_length=15)
    status = models.CharField(max_length=9)
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
