# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-06-12 09:27
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0006_jsonmodel'),
    ]

    operations = [
        migrations.DeleteModel(
            name='JSONModel',
        ),
    ]
