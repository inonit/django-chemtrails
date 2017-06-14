# -*- coding: utf-8 -*-

from django import forms
from django.conf.urls import url, include
from django.contrib import admin
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils.translation import ugettext_lazy as _

from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.views import AccessRuleViewSet, MetaGraphView
from chemtrails.neoutils.query import get_node_relationship_types


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):
    actions = ('toggle_active',)
    list_display = ('ctype_target', 'ctype_source', 'requires_staff', 'is_active', 'created')
    list_filter = ('requires_staff', 'is_active', 'ctype_target')
    filter_horizontal = ('permissions',)
    fieldsets = (
         (None, {'fields': ('ctype_source', 'ctype_target', 'description', 'permissions',
                            'relation_types', 'requires_staff', 'is_active')}),
         # ('Rule editor', {'fields': ('graph',)}),
    )
    formfield_overrides = {
        ArrayField: {'widget': forms.Textarea}
    }

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
