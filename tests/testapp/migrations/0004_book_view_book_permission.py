# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-04-06 21:59
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0003_publisher_custom_permission'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='book',
            options={'permissions': (('view_book', 'Can view book'),)},
        ),
    ]
