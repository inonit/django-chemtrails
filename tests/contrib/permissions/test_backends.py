# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, modify_settings

from chemtrails.contrib.permissions.models import AccessRule
from tests.utils import flush_nodes
from tests.testapp.autofixtures import Author, AuthorFixture, UserGenerator


class ChemtrailsPermissionBackendTestCase(TestCase):

    backend = 'chemtrails.contrib.permissions.backends.ChemtrailsPermissionBackend'

    def setUp(self):
        super(ChemtrailsPermissionBackendTestCase, self).setUp()
        self.patched_settings = modify_settings(
            AUTHENTICATION_BACKENDS={'append': self.backend}
        )
        self.patched_settings.enable()

    def tearDown(self):
        super(ChemtrailsPermissionBackendTestCase, self).tearDown()
        self.patched_settings.disable()

    @flush_nodes()
    def test_user_has_perm(self):
        author = AuthorFixture(Author).create_one()
        permission = Permission.objects.get(codename='change_author')
        author.user.user_permissions.add(permission)
        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_for_model(author.user),
            ctype_target=ContentType.objects.get_for_model(author),
            relation_types=['AUTHOR']
        )
        access_rule.permissions.add(permission)
        self.assertTrue(author.user.has_perm('testapp.change_author', author))
