# Generated by Django 3.0.8 on 2021-08-23 06:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0009_auto_20210705_2040'),
    ]

    operations = [
        migrations.CreateModel(
            name='BrightnessRules',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('device_name', models.CharField(default='D735', max_length=4)),
                ('mac_address', models.CharField(max_length=12)),
                ('ip_address', models.CharField(max_length=15)),
                ('min_value', models.IntegerField()),
                ('max_value', models.IntegerField()),
            ],
        ),
    ]
