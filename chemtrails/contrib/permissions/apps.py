# -*- coding: utf-8 -*-

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _

from corsheaders.signals import check_request_enabled


def cors_allow_api_admin(sender, request, **kwargs):
    return request.path.startswith('/admin/chemtrails_permissions/')


class ChemtrailsPermissionsConfig(AppConfig):
    name = 'chemtrails.contrib.permissions'
    verbose_name = _('Graph based permissions')
    label = 'chemtrails_permissions'

    def ready(self):
        check_request_enabled.connect(cors_allow_api_admin,
                                      dispatch_uid='chemtrails.contrib.permissions.cors_allow_api_admin')
