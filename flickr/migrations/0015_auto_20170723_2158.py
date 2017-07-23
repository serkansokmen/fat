# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-23 21:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('flickr', '0014_auto_20170723_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='image',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='flickr.Image'),
        ),
    ]
