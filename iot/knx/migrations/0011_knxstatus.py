# Generated by Django 3.0.8 on 2021-08-23 08:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('knx', '0010_brightnessrules'),
    ]

    operations = [
        migrations.CreateModel(
            name='KnxStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('groupaddress_name', models.CharField(max_length=50)),
                ('groupaddress', models.CharField(max_length=9)),
                ('datapoint_type', models.CharField(max_length=15)),
                ('status', models.CharField(max_length=9)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
            ],
        ),
    ]
