# -*- coding: utf-8 -*-
"""
Settings for django-chemtrails are all namespaced in
the CHEMTRAILS setting. For example:
CHEMTRAILS = {
    'ENABLED': True,
    'IGNORE_MODELS': [
        'migrations.migration',
    ]
}
"""
from django.conf import settings

from django.core.signals import setting_changed

# Following formats are supported:
#   - app_label: 'migrations' or 'migrations.*'
#   - specific:  'migrations.migration'
DEFAULTS = {
    'ENABLED': True,
    'MAX_CONNECTION_DEPTH': 1,
    'NAMED_RELATIONSHIPS': True,
    'CONNECT_META_NODES': False,
    'IGNORE_MODELS': [
        'admin.logentry',
        'migrations.migration',
    ],
}


class CSettings:

    def __init__(self, user_settings=None, defaults=None):
        if user_settings:
            self._user_settings = user_settings
        self.defaults = defaults or DEFAULTS

    def __getattr__(self, attr):
        if attr not in self.defaults:
            raise AttributeError('Invalid setting: \'%s\'' % attr)

        try:
            value = self.user_settings[attr]
        except KeyError:
            value = self.defaults[attr]

        # Cache the setting
        setattr(self, attr, value)
        return value

    @property
    def user_settings(self):
        if not hasattr(self, '_user_settings'):
            self._user_settings = getattr(settings, 'CHEMTRAILS', {})
        return self._user_settings

chemtrails_settings = CSettings(None, DEFAULTS)


def reload_settings(*args, **kwargs):
    global chemtrails_settings
    setting, value = kwargs['setting'], kwargs['value']
    if setting == 'CHEMTRAILS':
        chemtrails_settings = CSettings(value, DEFAULTS)

setting_changed.connect(reload_settings)
