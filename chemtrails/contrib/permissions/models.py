# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import models
from django.contrib.auth.models import Permission
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
    permissions = models.ManyToManyField(Permission, verbose_name=_('access rule permissions'), blank=True,
                                         help_text=_('Required permissions for target node.'),
                                         related_name='accessrule_permissions', related_query_name='accessrule')
    cypher = models.TextField(_('cypher query'), blank=True, help_text=_('Cypher query for ths access rule.'))
    is_active = models.BooleanField(default=True, help_text=_('Disable to disable evaluation of the rule '
                                                              'in the rule chain.'))
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)

    class Meta:
        pass

    def __str__(self):
        return self.cypher
