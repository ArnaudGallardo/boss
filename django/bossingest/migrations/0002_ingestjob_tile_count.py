# -*- coding: utf-8 -*-
# Generated by Django 1.9.1 on 2016-12-13 03:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bossingest', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingestjob',
            name='tile_count',
            field=models.IntegerField(default=0),
        ),
    ]
