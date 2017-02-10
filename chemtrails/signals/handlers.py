# -*- coding: utf-8 -*-

from django.conf import settings

from chemtrails.neoutils import get_model_string, get_relations_node_class_for_model, get_node_class_for_model
from chemtrails.settings import CHEMTRAILS_IGNORE_MODELS


def post_migrate_handler(sender, **kwargs):
    """
    Creates a Neo4j node representing the migrated apps models.
    """
    for model in sender.models.values():
        ModelRelationsNode = get_relations_node_class_for_model(model)
        ModelRelationsNode.sync()


def post_save_handler(sender, instance, created, **kwargs):
    """
    Keep the graph model in sync with the model
    """
    # Check if the model is in the ignore list.
    if not get_model_string(instance._meta.model) in getattr(
            settings, 'CHEMTRAILS_IGNORE_MODELS', CHEMTRAILS_IGNORE_MODELS):
        klass = get_node_class_for_model(instance._meta.model)
        klass(instance).sync()


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
