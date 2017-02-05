# -*- coding: utf-8 -*-

from django.utils import six

from neomodel import *
from .core import ModelRelationsMeta, ModelRelationsMixin

__all__ = [
    'ModelRelationsMeta',
    'ModelRelationsMixin',
    'get_relations_node_class_for_model',
    'get_node_class_for_model',
    'get_node_for_object'
]


def get_relations_node_class_for_model(model):
    """
    Get a ``ModelRelationsNode`` class for ``model``.
    :param model: Django model class.
    :returns: A ``StructuredNode`` class.
    """
    @six.add_metaclass(ModelRelationsMeta)
    class ModelRelationsNode(ModelRelationsMixin, StructuredNode):
        __metaclass_model__ = model

        class Meta:
            model = None  # Will pick model from parent class __metaclass_model__ attribute

    return ModelRelationsNode


def get_node_class_for_model(model):
    """
    Get a ``ModelNode`` class for ``model``.
    :param model: Django model class.
    :returns: A ``StructuredNode`` class.
    """
    raise NotImplemented


def get_node_for_object(instance):
    """
    Get a ``StructuredNode`` instance for the current instance.
    :param instance: Django model instance.
    :returns: A ``StructuredNode`` instance.
    """
    raise NotImplemented
