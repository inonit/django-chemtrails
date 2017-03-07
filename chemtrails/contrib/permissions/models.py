# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import models
from django.utils.translation import ugettext_lazy as _

from chemtrails.contrib.permissions.fields import ArrayChoiceField
from chemtrails.neoutils.query import get_node_relationship_types, get_node_permissions, get_relationship_types


def get_node_relations_choices():
    mapping = [(v, k) for k, v in get_node_relationship_types(params={'type': 'MetaNode'}).items()]
    return sorted(mapping, key=itemgetter(0))


def get_node_permissions_choices():
    mapping = [(v, _('%s' % v).capitalize()) for v in get_node_permissions()]
    return sorted(mapping, key=itemgetter(0))


def get_relationship_types_choices():
    mapping = [(v, _('%s' % v).upper()) for v in get_relationship_types()]
    return sorted(mapping, key=itemgetter(0))


class AccessRule(models.Model):

    source = ArrayChoiceField(models.CharField(max_length=100, blank=True), blank=True,
                              choices=get_node_relations_choices())
    target = ArrayChoiceField(models.CharField(max_length=100, blank=True), blank=True,
                              choices=get_node_relations_choices())
    action = models.CharField(max_length=20, choices=get_relationship_types_choices(), blank=True)
