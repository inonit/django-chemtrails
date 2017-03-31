# -*- coding: utf-8 -*-

from django.apps import apps
from django.conf.urls import url, include
from django.contrib import admin
from neomodel import db

from rest_framework import routers
from rest_framework.decorators import api_view
from rest_framework.response import Response

from chemtrails.contrib.permissions.forms import AccessRuleForm
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.serializers import NodeSerializer
from chemtrails.contrib.permissions.views import AccessRuleViewSet
from chemtrails.neoutils import get_meta_node_class_for_model
from chemtrails.neoutils.query import get_node_relationship_types
from chemtrails.utils import flatten


@admin.register(AccessRule)
class AccessRuleAdmin(admin.ModelAdmin):

    form = AccessRuleForm
    list_display = ('ctype_target', 'ctype_source', 'is_active', 'created')
    list_filter = ('is_active', 'ctype_target')
    filter_horizontal = ('permissions',)
    fieldsets = (
        (None, {'fields': ('ctype_source', 'ctype_target', 'permissions', 'query', 'is_active')}),
        ('Rule editor', {'fields': ('graph',)})
    )

    def get_form(self, request, obj=None, **kwargs):
        # TODO: Set session data for the widget
        return super(AccessRuleAdmin, self).get_form(request, obj, **kwargs)

    def get_urls(self):

        router = routers.DefaultRouter()
        router.register(r'access-rules', AccessRuleViewSet)

        info = self.model._meta.app_label, self.model._meta.model_name
        urlpatterns = [
            url(r'^neo4j/meta-graph/$', self.get_meta_graph_api_view, name='%s_%s_meta_graph' % info),
            url(r'^neo4j/nodelist/$', self.get_nodelist_api_view, name='%s_%s_nodelist' % info),
            url(r'^neo4j/', include(router.urls))
        ] + super(AccessRuleAdmin, self).get_urls()
        return urlpatterns

    @staticmethod
    @api_view(http_method_names=['GET'])
    def get_meta_graph_api_view(request):
        """
        Returns the Meta graph serialized as JSON.
        """
        result, _ = db.cypher_query('MATCH (n {type: "MetaNode"}) RETURN n')

        response = []
        for item in list(flatten(result)):
            try:
                if hasattr(item, 'properties') and all(value in item.properties for value in ('app_label', 'model_name')):
                    model = apps.get_model(app_label=item.properties['app_label'],
                                           model_name=item.properties['model_name'])
                    klass = get_meta_node_class_for_model(model)
                    serializer = NodeSerializer(instance=klass.inflate(item), many=False)
                    response.append(serializer.data)
            except LookupError:
                # Might trigger if getting data originating from a different source.
                continue
        return Response(data=response, content_type='application/json')

    @staticmethod
    @api_view(http_method_names=['GET'])
    def get_nodelist_api_view(request):
        params = {'type': 'MetaNode'}
        result = get_node_relationship_types(params)
        return Response(data=result)

