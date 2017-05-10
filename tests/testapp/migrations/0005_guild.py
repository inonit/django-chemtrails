# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2017-05-10 13:14
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('testapp', '0004_book_view_book_permission'),
    ]

    operations = [
        migrations.CreateModel(
            name='Guild',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('contact', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='guild_contacts', to='testapp.Author')),
                ('members', models.ManyToManyField(related_name='guild_set', to='testapp.Author', verbose_name='members')),
            ],
        ),
        migrations.AddField(
            model_name='author',
            name='guilds',
            field=models.ManyToManyField(blank=True, to='testapp.Guild'),
        ),
    ]
