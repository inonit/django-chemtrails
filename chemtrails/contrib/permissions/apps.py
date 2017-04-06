# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ChemtrailsPermissionsConfig(AppConfig):
    name = 'chemtrails.contrib.permissions'
    verbose_name = _('Graph based permissions')
    label = 'chemtrails_permissions'
