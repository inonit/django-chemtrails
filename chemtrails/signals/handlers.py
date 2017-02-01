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
    value = serializers.serialize('json', [instance])
    value = json.loads(value[1:-1])  # Trim off square brackets!
    brk = ''


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
