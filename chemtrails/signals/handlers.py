# -*- coding: utf-8 -*-

from chemtrails import settings
from chemtrails.neoutils import get_model_string, get_meta_node_for_model, get_node_for_object


def post_migrate_handler(sender, **kwargs):
    """
    Creates a Neo4j node representing the migrated apps models.
    """
    if settings.ENABLED is True:
        for model in sender.models.values():
            get_meta_node_for_model(model).sync(max_depth=1, update_existing=True)


def post_save_handler(sender, instance, **kwargs):
    """
    Keep the graph model in sync with the model.
    """
    if settings.ENABLED is True:
        if not get_model_string(instance._meta.model) in settings.IGNORE_MODELS:
            get_node_for_object(instance).sync(max_depth=1, update_existing=True)


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
