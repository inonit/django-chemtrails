# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase, modify_settings

from chemtrails.contrib.permissions.backends import ChemoPermissionsBackend
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.neoutils import get_nodeset_for_queryset

from tests.utils import clear_neo4j_model_nodes
from tests.testapp.autofixtures import Author, AuthorFixture, Store, StoreFixture

User = get_user_model()


class ChemoPermissionsBackendTestCase(TestCase):

    backend = 'chemtrails.contrib.permissions.backends.ChemoPermissionsBackend'

    def setUp(self):
        super(ChemoPermissionsBackendTestCase, self).setUp()
        self.patched_settings = modify_settings(
            AUTHENTICATION_BACKENDS={'append': self.backend}
        )
        self.patched_settings.enable()
        clear_neo4j_model_nodes()

    def tearDown(self):
        super(ChemoPermissionsBackendTestCase, self).tearDown()
        self.patched_settings.disable()
        clear_neo4j_model_nodes()

    def test_authenticate(self):
        kwargs = {
            'username': 'testuser',
            'password': 'test123.'
        }
        User.objects.create_user(**kwargs)

        backend = ChemoPermissionsBackend()
        self.assertIsNone(backend.authenticate(**kwargs))

    def test_get_all_permissions_user(self):
        permissions = Permission.objects.filter(content_type__app_label='auth',
                                                codename__in=[
                                                    'add_user', 'change_user',
                                                    'add_group', 'change_group'
                                                ])
        user = User.objects.create_user(username='testuser', password='test123.')
        group = Group.objects.create(name='group')
        user.user_permissions.add(*permissions)

        backend = ChemoPermissionsBackend()

        self.assertEqual(
            set(permissions.filter(content_type__model='group').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, group))
        )
        self.assertEqual(
            set(permissions.filter(content_type__model='user').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, user))
        )

    def test_get_all_permissions_group(self):
        permissions = Permission.objects.filter(content_type__app_label='auth',
                                                codename__in=[
                                                    'add_user', 'change_user',
                                                    'add_group', 'change_group'
                                                ])
        user = User.objects.create_user(username='testuser', password='test123.')
        group = Group.objects.create(name='group')
        group.user_set.add(user)
        group.permissions.add(*permissions)

        backend = ChemoPermissionsBackend()

        self.assertEqual(
            set(permissions.filter(content_type__model='group').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, group))
        )
        self.assertEqual(
            set(permissions.filter(content_type__model='user').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, user))
        )

    def test_get_all_permissions_mixed_user_and_group(self):
        permissions = Permission.objects.filter(content_type__app_label='auth',
                                                codename__in=[
                                                    'add_user', 'change_user',
                                                    'add_group', 'change_group'
                                                ])
        user = User.objects.create_user(username='testuser', password='test123.')
        group = Group.objects.create(name='group')
        group.user_set.add(user)

        user.user_permissions.add(*permissions.filter(content_type__model='user'))
        group.permissions.add(*permissions.filter(content_type__model='group'))

        backend = ChemoPermissionsBackend()

        self.assertEqual(
            set(permissions.filter(content_type__model='group').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, group))
        )
        self.assertEqual(
            set(permissions.filter(content_type__model='user').values_list('codename', flat=True)),
            set(backend.get_all_permissions(user, user))
        )

    def test_get_all_permissions_non_model_instance(self):
        class FooBar:
            pass

        obj = FooBar()
        user = User.objects.create_user(username='testuser', password='test123.')
        backend = ChemoPermissionsBackend()
        self.assertEqual(set(), backend.get_all_permissions(user, obj))

    def test_get_all_permissions_anonymous_user(self):
        class FooBar:
            pass

        obj = FooBar()
        user = AnonymousUser()
        backend = ChemoPermissionsBackend()
        self.assertEqual(set(), backend.get_all_permissions(user, obj))

    def test_has_perm_non_model_instance(self):
        class FooBar:
            pass

        obj = FooBar()
        user = User.objects.create_user(username='testuser', password='test123.')
        backend = ChemoPermissionsBackend()
        self.assertFalse(backend.has_perm(user, 'app_label.codename', obj))

    def test_has_perm_anonymous_user(self):
        user = AnonymousUser()
        group = Group.objects.create(name='group')

        backend = ChemoPermissionsBackend()
        self.assertFalse(backend.has_perm(user, 'app_label.codename', group))

    def test_check_permission(self):
        user = User.objects.create_user(username='testuser', password='test123.')

        group = Group.objects.create(name='group')
        group.user_set.add(user)

        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_for_model(User),
            ctype_target=ContentType.objects.get_for_model(Group),
            relation_types=[{'GROUPS': None}]
        )
        perm = Permission.objects.get(content_type__app_label='auth', codename='add_group')
        group.permissions.add(perm)
        access_rule.permissions.add(perm)

        backend = ChemoPermissionsBackend()
        self.assertTrue(backend.has_perm(user, 'add_group', group))       # Permission codename only
        self.assertTrue(backend.has_perm(user, 'auth.add_group', group))  # Full permission string

    def test_user_has_perm_single_relation_type(self):
        author = AuthorFixture(Author).create_one()
        permission = Permission.objects.get(codename='change_author')
        author.user.user_permissions.add(permission)
        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_for_model(author.user),
            ctype_target=ContentType.objects.get_for_model(author),
            relation_types=[{'AUTHOR': None}]
        )
        access_rule.permissions.add(permission)
        self.assertTrue(author.user.has_perm('testapp.change_author', author))

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
            relation_types=[{'AUTHOR': None}, {'BOOK': None}, {'STORE': None}]
        )
        access_rule.permissions.add(*list(permissions.exclude(codename='delete_store')))

        self.assertTrue(user.has_perm('testapp.add_store', store))
        self.assertTrue(user.has_perm('testapp.change_store', store))
        self.assertFalse(user.has_perm('testapp.delete_store', store))
