# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, modify_settings

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.neoutils import get_nodeset_for_queryset

from tests.utils import flush_nodes
from tests.testapp.autofixtures import Author, AuthorFixture, Store, StoreFixture


class ChemoPermissionsBackendTestCase(TestCase):

    backend = 'chemtrails.contrib.permissions.backends.ChemoPermissionsBackend'

    def setUp(self):
        super(ChemoPermissionsBackendTestCase, self).setUp()
        self.patched_settings = modify_settings(
            AUTHENTICATION_BACKENDS={'append': self.backend}
        )
        self.patched_settings.enable()

    def tearDown(self):
        super(ChemoPermissionsBackendTestCase, self).tearDown()
        self.patched_settings.disable()

    @flush_nodes()
    def test_user_has_perm_single_relation_type(self):
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

    @flush_nodes()
    def test_user_has_perm_multiple_relation_types(self):
        # Set up a bookstore graph
        store = StoreFixture(Store).create_one()
        get_nodeset_for_queryset(Store.objects.filter(pk=store.pk), sync=True)
        permissions = Permission.objects.filter(codename__in=['add_store', 'change_store', 'delete_store'])

        user = get_user_model().objects.latest('pk')
        user.user_permissions.add(*list(permissions))

        # Create an access rule which allows 'add_store' and 'change_store',
        # but not 'delete_store'
        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_for_model(user),
            ctype_target=ContentType.objects.get_for_model(Store),
            relation_types=['AUTHOR', 'BOOK', 'STORE']
        )
        access_rule.permissions.add(*list(permissions.exclude(codename='delete_store')))

        self.assertTrue(user.has_perm('testapp.add_store', store))
        self.assertTrue(user.has_perm('testapp.change_store', store))
        self.assertFalse(user.has_perm('testapp.delete_store', store))


