# -*- coding: utf-8 -*-

from django import forms
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.utils.text import Truncator

from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.views import AccessRuleViewSet, MetaGraphView
from chemtrails.contrib.permissions.forms import CypherWidget
from chemtrails.neoutils.query import get_node_relationship_types
from chemtrails.neoutils import get_node_for_object
from chemtrails.neoutils.query import validate_cypher


class AccessRuleForm(forms.ModelForm):

    cypher_statement = forms.CharField(widget=CypherWidget, required=False,
                                       help_text=_('Preview the generated cypher statement. Any changes done in '
                                                   'this view will <b>not</b> be saved. <br />Note that this '
                                                   'is generated using a mock source node, which means that filter '
                                                   'parameters will be replaced with real values on evaluation.'
                                                   ''))

    class Meta:
        model = AccessRule
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        kwargs['initial'] = {'cypher_statement': self.get_statement(kwargs.get('instance', None))}
        super(AccessRuleForm, self).__init__(*args, **kwargs)

    def get_statement(self, instance=None):
        if not isinstance(instance, self._meta.model):
            return ''

        # TODO: This should be DRY'ed up!
        fake_model = instance.ctype_source.model_class()(pk=0)
        manager = get_node_for_object(fake_model).paths
        error_message = _('Unable to validate cypher statement.\nError was: "%(error)s".')

        query = None
        for n, rule_definition in enumerate(instance.relation_types_obj):
            relation_type, target_props = zip(*rule_definition.items())
            relation_type, target_props = relation_type[0], target_props[0]  # TODO: This should be validated before save!

            source_props = {}
            if n == 0 and instance.requires_staff:
                source_props.update({'is_staff': True})
            try:
                manager = manager.add(relation_type, source_props=source_props, target_props=target_props)
            except (ValueError, AttributeError) as e:
                return error_message % {'error': e}

        if manager.statement:
            query = manager.get_match()

        try:
            if query:
                validate_cypher(query, raise_exception=True, exc_class=ValidationError)
        except ValidationError as e:
            return error_message % {'error': e}
        return query


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    form = AccessRuleForm
    actions = ('toggle_active',)
    list_display = ('get_short_description', 'ctype_target', 'ctype_source',
                    'requires_staff', 'is_active', 'updated')
    list_filter = ('requires_staff', 'is_active', 'ctype_target')
    filter_horizontal = ('permissions',)
    fieldsets = (
        (None, {'fields': ('ctype_source', 'ctype_target', 'description', 'permissions',
                           'relation_types', 'cypher_statement', 'requires_staff', 'is_active')}),
        ('Dates', {'fields': ('created', 'updated')})
        # ('Rule editor', {'fields': ('graph',)}),
    )
    formfield_overrides = {
        ArrayField: {'widget': forms.Textarea}
    }
    readonly_fields = ('created', 'updated')

    def toggle_active(self, request, queryset):
        """
        Inverts the ``is_active`` flag of chosen access rules.
        """
        queryset.update(
            is_active=models.Case(
                models.When(is_active=True, then=models.Value(False)),
                default=models.Value(True)))
        self.message_user(request, _('Activated {0} and deactivated {1} '
                                     'access rules.'.format(queryset.filter(is_active=True).count(),
                                                            queryset.filter(is_active=False).count())))
    toggle_active.short_description = _('Toggle active or inactive access rules')

    def get_short_description(self, obj):
        return Truncator(obj.description).chars(55)

    def get_urls(self):

        router = routers.DefaultRouter()
        router.register(r'access-rules', AccessRuleViewSet)
        router.register(r'meta-graph', MetaGraphView, base_name='metagraph')

        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            url(r'^neo4j/nodelist/$', self.get_nodelist_api_view, name='%s_%s_nodelist' % info),  # Deprecated
            url(r'^neo4j/', include(router.urls))
        ] + super(AccessRuleAdmin, self).get_urls()
        return urlpatterns

    @staticmethod
    @api_view(http_method_names=['GET'])
    def get_nodelist_api_view(request):
        # TODO: This should be removed!!
        params = {'type': 'MetaNode'}
        result = get_node_relationship_types(params)
        return Response(data=result)
