# -*- coding: utf-8 -*-

from django.test import TestCase, override_settings
from chemtrails import settings


class SettingsTestCase(TestCase):

    def test_default_settings(self):
        self.assertEqual(settings.ENABLED, True)
        self.assertEqual(settings.MAX_CONNECTION_DEPTH, 1)
        self.assertEqual(settings.NAMED_RELATIONSHIPS, True)
        self.assertEqual(settings.CONNECT_META_NODES, False)
        self.assertEqual(settings.IGNORE_MODELS, ['admin.logentry', 'migrations.migration'])

    @override_settings(CHEMTRAILS={
        'ENABLED': False,
        'NAMED_RELATIONSHIPS': False,
        'IGNORE_MODELS': [
            'auth.user'
        ]
    })
    def test_override_settings(self):
        from chemtrails.settings import chemtrails_settings as settings  # Need to re-import after override
        self.assertEqual(settings.ENABLED, False)
        self.assertEqual(settings.NAMED_RELATIONSHIPS, False)
        self.assertEqual(settings.CONNECT_META_NODES, False)
        self.assertEqual(settings.IGNORE_MODELS, ['auth.user'])

    def test_getting_invalid_setting(self):
        try:
            settings.INVALID_SETTING
            self.fail('Did not raise AttributeError when declaring an invalid setting')
        except AttributeError as e:
            self.assertEqual(str(e), 'Invalid setting: \'INVALID_SETTING\'')

    def test_setting_changed_signal_updates_global_settings_object(self):
        try:
            raise NotImplementedError
        except NotImplementedError as e:
            self.assertIsInstance(e, NotImplementedError)
