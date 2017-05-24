# -*- coding: utf-8 -*-

from chemtrails import settings
from chemtrails.neoutils import (
    get_meta_node_for_model,
    get_node_for_object, get_node_class_for_model, get_nodeset_for_queryset
)


def post_migrate_handler(sender, **kwargs):
    """
    Create the meta graph after migrations has been installed.
    """
    if settings.ENABLED:
        for model in sender.models.values():
            get_meta_node_for_model(model).sync(max_depth=settings.MAX_CONNECTION_DEPTH, update_existing=True)


def post_save_handler(sender, instance, **kwargs):
    """
    Sync the node instance after it has been saved.
    """
    if settings.ENABLED:
        get_node_for_object(instance).sync(max_depth=settings.MAX_CONNECTION_DEPTH, update_existing=True)


def pre_delete_handler(sender, instance, **kwargs):
    """
    Delete the node from the graph before it is removed from the database.
    """
    if settings.ENABLED:
        klass = get_node_class_for_model(instance._meta.model)
        node = klass.nodes.get_or_none(**{'pk': instance.pk})
        if node:
            node.delete()


def m2m_changed_handler(sender, instance, action, reverse, model, pk_set, **kwargs):
    """
    Update relations for the node when m2m relationships are added or deleted.
    """
    if settings.ENABLED:
        if action not in ('post_add', 'post_remove', 'post_clear'):
            return

        if action == 'post_add':
            get_nodeset_for_queryset(model.objects.filter(pk__in=pk_set), sync=True,
                                     max_depth=settings.MAX_CONNECTION_DEPTH)
        elif action == 'post_remove':
            get_nodeset_for_queryset(model.objects.filter(pk__in=pk_set), sync=True,
                                     max_depth=settings.MAX_CONNECTION_DEPTH)
        elif action == 'post_clear':
            get_node_for_object(instance).sync(max_depth=settings.MAX_CONNECTION_DEPTH, update_existing=True)
