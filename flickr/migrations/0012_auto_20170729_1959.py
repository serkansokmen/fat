# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-07-29 19:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('flickr', '0011_auto_20170729_1959'),
    ]

    operations = [
        migrations.AlterField(
            model_name='annotation',
            name='objects',
            field=models.ManyToManyField(blank=True, to='flickr.ObjectX'),
        ),
    ]
