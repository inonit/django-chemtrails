# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import models

from chemtrails.contrib.permissions.fields import ArrayChoiceField
from chemtrails.neoutils.query import get_node_relationship_types


def get_node_relations_choices():
    mapping = [(v, k) for k, v in get_node_relationship_types(params={'type': 'ModelNode'}).items()]
    return sorted(mapping, key=itemgetter(0))


class AccessRule(models.Model):

    related_through = ArrayChoiceField(models.CharField(max_length=100, blank=True), blank=True,
                                       choices=get_node_relations_choices())
