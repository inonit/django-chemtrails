# -*- coding: utf-8 -*-

from django.apps import apps
from django.conf.urls import url
from django.contrib import admin
from django.http import JsonResponse

from neomodel import db
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chemtrails.neoutils import get_meta_node_class_for_model
from chemtrails.neoutils.query import get_node_relationship_types
from chemtrails.contrib.permissions.api.serializers import NodeSerializer
from chemtrails.contrib.permissions.forms import AccessRuleForm
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.utils import flatten


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

    @staticmethod
    @api_view()
    def get_neo4j_query_api_view(request):
        response = []
        query = request.GET.get('query', None)
        if query:
            result, _ = db.cypher_query(query)
            for item in list(flatten(result)):
                try:
                    if hasattr(item, 'properties') and all(
                                    value in item.properties for value in ('app_label', 'model_name')):
                        model = apps.get_model(app_label=item.properties['app_label'],
                                               model_name=item.properties['model_name'])
                        klass = get_meta_node_class_for_model(model)
                        serializer = NodeSerializer(instance=klass.inflate(item), many=False)
                        response.append(serializer.data)
                except LookupError:
                    continue
        return Response(response)

    def get_nodelist_api_view(self, request):
        params = {'type': 'MetaNode'}
        result = get_node_relationship_types(params)
        return JsonResponse(data=result)

    def get_nodetype_relations(self, request, node_type):
        pass


class AlchemyJSResponse(JsonResponse):
    pass
