# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-06-02 05:14
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('dengue_linebot', '0023_auto_20170309_1013'),
    ]

    operations = [
        migrations.AddField(
            model_name='lineuser',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(default='POINT(0.0 0.0)', geography=True, srid=4326),
        ),
        migrations.AlterField(
            model_name='botreplylog',
            name='receiver',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bot_reply_log', to='dengue_linebot.LineUser'),
        ),
        migrations.AlterField(
            model_name='govreport',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='gov_faculty', to='dengue_linebot.LineUser'),
        ),
        migrations.AlterField(
            model_name='messagelog',
            name='speaker',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='message_log', to='dengue_linebot.LineUser'),
        ),
        migrations.AlterField(
            model_name='suggestion',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='suggestion', to='dengue_linebot.LineUser'),
        ),
    ]
