# Generated by Django 3.1.2 on 2021-07-05 20:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0005_auto_20210705_2019'),
    ]

    operations = [
        migrations.AlterField(
            model_name='alsstatus',
            name='time_stamp',
            field=models.DateTimeField(default=datetime.datetime(2021, 7, 5, 20, 24, 25, 734406), null=True),
        ),
    ]
