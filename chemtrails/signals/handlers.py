# -*- coding: utf-8 -*-

import json
from django.core import serializers
from django.utils import six

from neomodel import *

from chemtrails.neoutils import ModelRelationsMeta, ModelRelationsMixin


def post_migrate_handler(sender, **kwargs):
    """
    Make sure all StructuredNode labels are installed.
    """
    for model in sender.models.values():

        # Define a ModelRelationsNode class representing the model relations.
        @six.add_metaclass(ModelRelationsMeta)
        class ModelNode(ModelRelationsMixin, StructuredNode):

            __metaclass_model__ = model

            class Meta:
                model = None  # Will pick model from parent __metaclass_model__

        # This will create-or-update the node.
        ModelNode.sync()

    # TODO: Should read from settings.py
    install_all_labels()


def post_save_handler(sender, instance, created, **kwargs):
    """
    Get all relations the current instance has and store them in the graph.
    """
    serialized = serializers.serialize('json', [instance])
    serialized = json.loads(serialized[1:-1])  # Trim off square brackets!

    # TODO: Write to graph


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
