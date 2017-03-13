# -*- coding: utf-8 -*-
import json

from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse

from neomodel import db

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
            url(r'^neo4j-query/$', self.get_neo4j_query_api_view, name='%s_%s_neo4j_query' % info),
            url(r'^nodelist/$', self.get_nodelist_api_view, name='%s_%s_nodelist' % info),
            url(r'^(?P<node_type>.+)/relations/$', self.get_nodetype_relations,
                name='%s_%s_nodetype_relations' % info),
        ] + super(AccessRuleAdmin, self).get_urls()
        return urlpatterns

    @staticmethod
    def sanitize_query(params):
        return params

    def get_neo4j_query_api_view(self, request):
        query = request.GET.get('query', None)
        if query:
            result, _ = db.cypher_query(query)
            try:
                return AlchemyJSResponse(data={})
            except Exception as e:
                pass
        return AlchemyJSResponse(data={})

    def get_nodelist_api_view(self, request):
        params = {'type': 'MetaNode'}
        result = get_node_relationship_types(params)
        return JsonResponse(data=result)

    def get_nodetype_relations(self, request, node_type):
        pass


class AlchemyJSResponse(JsonResponse):
    pass
