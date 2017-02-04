# -*- coding: utf-8 -*-

from django.utils import six
from neomodel import *

from chemtrails.neoutils import ModelRelationsMeta, ModelRelationsMixin


def get_node_class_for_model(model):

    @six.add_metaclass(ModelRelationsMeta)
    class ModelNode(ModelRelationsMixin, StructuredNode):
        __metaclass_model__ = model

        class Meta:
            model = None

    return ModelNode

