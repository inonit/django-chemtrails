# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-02 10:43
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0005_author_test'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='author',
            name='test',
        ),
    ]
