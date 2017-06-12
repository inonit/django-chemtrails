# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.db import models

from chemtrails.contrib.permissions.forms import JSONField


class Author(models.Model):
    user = models.OneToOneField('auth.User')
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    guilds = models.ManyToManyField('testapp.Guild', blank=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    tag = models.CharField(max_length=20)
    content_type = models.ForeignKey(ContentType, verbose_name='content type',
                                     related_name='content_type_set_for_%(class)s')
    object_pk = models.IntegerField(verbose_name='object ID')
    content_object = GenericForeignKey('content_type', 'object_pk')

    def __str__(self):
        return self.tag


class Publisher(models.Model):
    name = models.CharField(max_length=300)
    num_awards = models.IntegerField()

    class Meta:
        permissions = (
            ('can_publish', 'Can publish'),
        )

    def __str__(self):
        return self.name


class Book(models.Model):
    name = models.CharField(max_length=300)
    pages = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    rating = models.FloatField()
    authors = models.ManyToManyField(Author)
    tags = GenericRelation(Tag, object_id_field='object_pk', content_type_field='content_type')
    publisher = models.ForeignKey(Publisher)
    pubdate = models.DateField()

    class Meta:
        permissions = (
            ('view_book', 'Can view book'),
        )

    def __str__(self):
        return self.name


class Store(models.Model):
    name = models.CharField(max_length=300)
    books = models.ManyToManyField(Book)
    bestseller = models.ForeignKey(Book, related_name='bestseller_stores', null=True, blank=True)
    registered_users = models.PositiveIntegerField()

    def __str__(self):
        return self.name


class Guild(models.Model):
    name = models.CharField(max_length=100)
    contact = models.ForeignKey(Author, related_name='guild_contacts')
    members = models.ManyToManyField(Author, verbose_name='members', related_name='guild_set')

#
# class JSONModel(models.Model):
#     json = JSONField()
