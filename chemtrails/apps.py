# -*- coding: utf-8 -*-

import os

from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import m2m_changed, post_migrate, post_save, pre_delete

from neomodel import config

config.AUTO_INSTALL_LABELS = False


class ChemtrailsConfig(AppConfig):
    name = 'chemtrails'

    def ready(self):
        from .signals.handlers import (
            m2m_changed_handler, post_migrate_handler,
            post_save_handler, pre_delete_handler
        )

        m2m_changed.connect(receiver=m2m_changed_handler,
                            dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
        post_save.connect(receiver=post_save_handler,
                          dispatch_uid='chemtrails.signals.handlers.post_save_handler')
        pre_delete.connect(receiver=pre_delete_handler,
                           dispatch_uid='chemtrails.signals.handlers.pre_delete_handler')

        post_migrate.connect(receiver=post_migrate_handler,
                             dispatch_uid='neomodel.core.post_migrate_handler')

        # Neo4j config
        config.DATABASE_URL = getattr(settings, 'NEO4J_BOLT_URL',
                                      os.environ.get('NEO4J_BOLT_URL', config.DATABASE_URL))
        config.FORCE_TIMEZONE = getattr(settings, 'NEO4J_FORCE_TIMEZONE',
                                        os.environ.get('NEO4J_FORCE_TIMEZONE', False))
