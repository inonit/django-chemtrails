# -*- coding: utf-8 -*-

import json
from django.core import serializers
from neomodel import *

from chemtrails.neoutils import get_relations_node_class_for_model


def post_migrate_handler(sender, **kwargs):
    """
    Creates a Neo4j node representing the migrated apps models.
    """
    for model in sender.models.values():
        ModelRelationsNode = get_relations_node_class_for_model(model)
        ModelRelationsNode.sync()

    # TODO: Should read from settings.py
    install_all_labels()


def post_save_handler(sender, instance, created, **kwargs):
    """
    Keep the graph model in sync with the model
    """
    serialized = serializers.serialize('json', [instance])
    serialized = json.loads(serialized[1:-1])  # Trim off square brackets!

    # TODO: Write to graph


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
