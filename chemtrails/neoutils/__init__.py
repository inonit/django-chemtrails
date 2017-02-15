# -*- coding: utf-8 -*-

from django.utils import six

from neomodel import *
from .core import (
    ModelNodeMeta, ModelNodeMixin,
    MetaNodeMeta, MetaNodeMixin,
    get_model_string
)

__all__ = [
    'get_meta_node_class_for_model',
    'get_node_class_for_model',
    'get_node_for_object',
    'get_model_string',
    'model_cache'
]
model_cache = {}


def get_meta_node_class_for_model(model):
    """
    Meta nodes are used to generate a map of the relationships
    in the database. There's only a single MetaNode per model.
    :param model: Django model class.
    :returns: A ``StructuredNode`` class.
    """
    cache_key = '{object_name}RelationMeta'.format(object_name=model._meta.object_name)
    if cache_key in model_cache:
        return model_cache[cache_key]
    else:
        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            __metaclass_model__ = model

            class Meta:
                model = None  # Will pick model from parent class __metaclass_model__ attribute

        model_cache[cache_key] = MetaNode
        return MetaNode


def get_node_class_for_model(model):
    """
    Model nodes represent a model instance in the database.
    :param model: Django model class.
    :returns: A ``ModelNode`` class.
    """
    cache_key = '{object_name}Node'.format(object_name=model._meta.object_name)
    if cache_key in model_cache:
        return model_cache[cache_key]
    else:
        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            __metaclass_model__ = model

            class Meta:
                model = None  # Will pick model from parent class __metaclass_model__ attribute

        model_cache[cache_key] = ModelNode
        return ModelNode


def get_node_for_object(instance):
    """
    Get a ``ModelNode`` instance for the current object instance.
    :param instance: Django model instance.
    :returns: A ``ModelNode`` instance.
    """
    ModelNode = get_node_class_for_model(instance._meta.model)
    return ModelNode(instance=instance)

