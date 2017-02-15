# -*- coding: utf-8 -*-

from django.utils import six

from neomodel import *
from .core import (
    ModelNodeBase,
    ModelNodeMeta, ModelNodeMixin,
    ModelRelationsMeta, ModelRelationsMixin,
    get_model_string
)

__all__ = [
    'get_relations_node_class_for_model',
    'get_node_class_for_model',
    'get_node_for_object',
    'get_model_string',
    'model_cache'
]
model_cache = {}


def get_relations_node_class_for_model(model):
    """
    Get a ``ModelRelationsNode`` class for ``model``.
    :param model: Django model class.
    :returns: A ``StructuredNode`` class.
    """
    cache_key = '{object_name}RelationMeta'.format(object_name=model._meta.object_name)
    if cache_key in model_cache:
        return model_cache[cache_key]
    else:
        @six.add_metaclass(ModelRelationsMeta)
        class ModelRelationsNode(ModelRelationsMixin, StructuredNode):
            __metaclass_model__ = model

            class Meta:
                model = None  # Will pick model from parent class __metaclass_model__ attribute

        model_cache[cache_key] = ModelRelationsNode
        return ModelRelationsNode


def get_node_class_for_model(model):
    """
    Get a ``ModelNode`` class for ``model``.
    :param model: Django model class.
    :returns: A ``StructuredNode`` class.
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
    Get a ``StructuredNode`` _instance for the current _instance.
    :param instance: Django model _instance.
    :returns: A ``StructuredNode`` _instance.
    """
    ModelNode = get_node_class_for_model(instance._meta.model)
    return ModelNode(instance=instance)

