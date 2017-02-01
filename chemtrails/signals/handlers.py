# -*- coding: utf-8 -*-

import json
from neomodel.core import install_all_labels
from django.core import serializers


def post_migrate_handler(sender, **kwargs):
    """
    Make sure all StructuredNode labels are installed.
    """
    install_all_labels()


def post_save_handler(sender, instance, created, **kwargs):
    """
    Get all relations the current instance has and store them in the graph.
    """
    # Ref: https://docs.djangoproject.com/en/1.10/ref/models/meta/

    from chemtrails.utils import NeoModelWrapper
    i = NeoModelWrapper(instance).get_neo_model()
    if hasattr(i, 'someinteger'):
        i.someinteger = 1
        i.save()


    # fields = instance._meta.get_fields(include_hidden=True)
    # fields = [
    #     (f, f.model if f.model != instance else None)
    #     for f in instance._meta.get_fields()
    #     if f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
    # ]
    # if fields:
    #     brk = ''
    serialized = serializers.serialize('json', [instance])
    serialized = json.loads(serialized[1:-1])  # Trim off square brackets!


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
