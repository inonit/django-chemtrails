# -*- coding: utf-8 -*-

from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse

from chemtrails.neoutils.query import get_node_relationship_types
from chemtrails.contrib.permissions.forms import AccessRuleForm
from chemtrails.contrib.permissions.models import AccessRule


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):

    form = AccessRuleForm

    def get_form(self, request, obj=None, **kwargs):
        # TODO: Set session data for the widget
        return super(AccessRuleAdmin, self).get_form(request, obj, **kwargs)

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            url(r'^nodelist/$', self.get_nodelist_api_view, name='%s_%s_nodelist' % info),
            url(r'^(?P<node_type>.+)/relations/$', self.get_nodetype_relations,
                name='%s_%s_nodetype_relations' % info),
        ] + super(AccessRuleAdmin, self).get_urls()
        return urlpatterns

    def get_nodelist_api_view(self, request):
        params = {'type': 'MetaNode'}
        result = get_node_relationship_types(params)
        return JsonResponse(data=result)

    def get_nodetype_relations(self, request, node_type):
        pass

