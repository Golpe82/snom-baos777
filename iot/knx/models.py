from django.db import models

# class KnxStatus(models.Model):
#     groupaddress_name = models.CharField(max_length=50)
#     groupaddress = models.CharField(max_length=9)
#     datapointtype = models.CharField(max_length=15)
#     value = models.CharField(max_length=9)
#     timestamp = 

#     pass

class AlsStatus(models.Model):
    device_name = "D735"
    mac_address = models.CharField(max_length=12)
    ip_address = models.CharField(max_length=15)
    raw_value = models.IntegerField()
    value = models.FloatField()
    time_stamp = models.DateTimeField()
     


# class Rules(models.Model):

#     pass
