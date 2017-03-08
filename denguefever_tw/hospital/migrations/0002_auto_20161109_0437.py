# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-11-09 04:37
from __future__ import unicode_literals

from django.db import migrations

import django.contrib.gis.db.models.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hospital', '0001_initial'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='hospital',
            unique_together=set([('name', 'address', 'location')]),
        ),
    ]
