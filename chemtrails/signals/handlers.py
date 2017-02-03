# -*- coding: utf-8 -*-

import json
from neomodel.core import install_all_labels
from django.core import serializers

from chemtrails.utils import ModelRelationWrapper


def post_migrate_handler(sender, **kwargs):
    """
    Make sure all StructuredNode labels are installed.
    """
    # for model in sender.models.values():
    #     ModelRelationWrapper(model).save()

    install_all_labels()


def post_save_handler(sender, instance, created, **kwargs):
    """
    Get all relations the current instance has and store them in the graph.
    """
    serialized = serializers.serialize('json', [instance])
    serialized = json.loads(serialized[1:-1])  # Trim off square brackets!


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
