# -*- coding: utf-8 -*-
# Generated by Django 1.11.3 on 2017-08-07 19:05
from __future__ import unicode_literals

from django.db import migrations
import uuid


def gen_uuid(apps, schema_editor):
    MarkedObject = apps.get_model('flickr', 'MarkedObject')
    for row in MarkedObject.objects.all():
        row.uuid = uuid.uuid4()
        row.save(update_fields=['uuid'])


class Migration(migrations.Migration):

    dependencies = [
        ('flickr', '0005_markedobject_uuid'),
    ]

    operations = [
        # omit reverse_code=... if you don't want the migration to be reversible.
        migrations.RunPython(gen_uuid, reverse_code=migrations.RunPython.noop),
    ]