# -*- coding: utf-8 -*-

from django.apps import apps

from neomodel import db

from rest_framework.response import Response
from rest_framework.viewsets import ViewSet, ModelViewSet

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.serializers import AccessRuleSerializer, NodeSerializer
from chemtrails.neoutils import get_meta_node_class_for_model
from chemtrails.utils import flatten


class AccessRuleViewSet(ModelViewSet):
    """
    API View for access rules.
    """
    # authentication_classes = ()
    # permission_classes = ()
    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer


class MetaGraphView(ViewSet):
    """
    API View for getting the meta graph.
    """
    # authentication_classes = ()
    # permission_classes = ()

    def list(self, request, format=None):
        """
        Returns the meta graph serialized as JSON.
        """
        result, _ = db.cypher_query('MATCH (n {type: "MetaNode", is_intermediary: False}) RETURN n')

        response = []
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
                # Might trigger if getting data originating from a different source.
                continue
        return Response(data=response, content_type='application/json')
