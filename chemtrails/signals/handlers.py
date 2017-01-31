# -*- coding: utf-8 -*-

from neomodel.core import install_all_labels


def post_migrate_handler(sender, **kwargs):
    """
    Make sure all StructuredNode labels are installed.
    """
    install_all_labels()


def post_save_handler(sender, instance, created, **kwargs):
    pass


def pre_delete_handler(sender, instance, **kwargs):
    pass


def m2m_changed_handler(sender, instance, action, reverse, pk_set, **kwargs):
    pass
