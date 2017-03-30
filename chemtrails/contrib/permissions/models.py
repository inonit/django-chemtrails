# -*- coding: utf-8 -*-

from operator import itemgetter

from django.db import models
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import ugettext_lazy as _

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
    ctype_source = models.ForeignKey(ContentType, verbose_name=_('source content type'),
                                     related_name='accessrule_ctype_source_set')
    ctype_target = models.ForeignKey(ContentType, verbose_name=_('target content type'),
                                     related_name='accessrule_ctype_target_set')
    permissions = models.ManyToManyField(Permission, verbose_name=_('access rule permissions'), blank=True,
                                         help_text=_('Required permissions for target node.'),
                                         related_name='accessrule_permissions', related_query_name='accessrule')
    query = models.TextField(_('cypher query'), blank=True, help_text=_('Cypher query for ths access rule.'))
    is_active = models.BooleanField(default=True, help_text=_('Disable to disable evaluation of the rule '
                                                              'in the rule chain.'))
    created = models.DateTimeField(verbose_name=_('created'), auto_now_add=True)
    updated = models.DateTimeField(verbose_name=_('updated'), auto_now=True)

    class Meta:
        ordering = ('ctype_target', '-created',)

    def __repr__(self):
        return '<%(class)s: [%(source)s]-[*]-[%(target)s]>' % {
            'class': self.__class__.__name__,
            'source': '%s.%s' % (self.ctype_source.app_label, self.ctype_source.model),
            'target': '%s.%s' % (self.ctype_target.app_label, self.ctype_target.model),
        }

    # def __str__(self):
        # return '{source}-{target}: {query}'.format(source=self.ctype_source, target=self.ctype_target)
