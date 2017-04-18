# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from chemtrails.contrib.permissions import utils
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.neoutils import get_nodeset_for_queryset
from tests.testapp.autofixtures import Book, BookFixture, Store, StoreFixture
from tests.utils import flush_nodes

User = get_user_model()


class GetIdentityTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.get_identity()``.
    """

    def test_get_identity_anonymous_user(self):
        user = AnonymousUser()
        try:
            utils.get_identity(user)
            self.fail('Did not raise NotImplementedError when checking with AnonymousUser.')
        except NotImplementedError as e:
            self.assertEqual(str(e), 'Implement support for AnonymousUser, please!')

    def test_get_identity_user(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        self.assertEqual(utils.get_identity(user), (user, None))

    def test_get_identity_group(self):
        group = Group.objects.create(name='mygroup')
        self.assertEqual(utils.get_identity(group), (None, group))


class GetContentTypeTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.get_content_type()``.
    """

    def test_get_content_type_from_class(self):
        self.assertEqual(utils.get_content_type(User),
                         ContentType.objects.get_for_model(User))

    def test_get_content_type_from_instance(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        self.assertEqual(utils.get_content_type(user),
                         ContentType.objects.get_for_model(User))


class CheckPermissionsAppLabelTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.check_permissions_app_label()``.
    """

    def test_check_permissions_app_label_single(self):
        perm = 'testapp.add_book'
        book = BookFixture(Book).create_one()
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(book), ['add_book']))
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(Book), ['add_book']))

    def test_check_permissions_app_label_invalid_fails(self):
        perm = 'testapp.invalid_permission'
        self.assertRaisesMessage(ContentType.DoesNotExist, '', utils.check_permissions_app_label, permissions=perm)

    def test_check_permissions_app_label_sequence(self):
        perms = ['testapp.add_book', 'testapp.change_book']
        book = BookFixture(Book).create_one()

        ctype, codenames = utils.check_permissions_app_label(perms)
        self.assertEqual(ctype, utils.get_content_type(book))
        self.assertEqual(sorted(codenames), ['add_book', 'change_book'])

    def test_check_permissions_app_label_sequence_fails(self):
        perms = ['testapp.add_book', 'testapp.add_store']
        self.assertRaisesMessage(
            ValueError, ('Calculated content type from permission "testapp.add_store" '
                         'store does not match <ContentType: book>.'),
            utils.check_permissions_app_label, permissions=perms)


class GetObjectsForUserTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.get_objects_for_user()``.
    """

    @flush_nodes()
    def test_get_objects_for_user(self):
        graph1 = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                 StoreFixture(Store).create(count=1, commit=True)))
        get_nodeset_for_queryset(graph1, sync=True, max_depth=1)
        graph1_user_pks = list(User.objects.values_list('pk', flat=True))

        graph2 = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                 StoreFixture(Store).create(count=1, commit=True)))
        get_nodeset_for_queryset(graph2, sync=True, max_depth=1)
        graph2_user_pks = list(User.objects.exclude(pk__in=graph1_user_pks).values_list('pk', flat=True))

        # Check if a user in the graph can get a path to all other users in the graph.
        permission = Permission.objects.get(codename='change_user')
        user = User.objects.get(pk=graph1_user_pks[0])
        user.user_permissions.add(permission)

        # Create an access rule from User to User following a path
        rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                         ctype_target=utils.get_content_type(User),
                                         relation_types=[
                                             'AUTHOR', 'BOOK',
                                             'STORE', 'BOOKS',
                                             'AUTHORS', 'USER'
                                         ])
        rule.permissions.add(permission)

        permitted_users = utils.get_objects_for_user(user=user, permissions='auth.change_user')
        brk = ''


class GetObjectsForGroupTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.get_objects_for_group()``.
    """
    pass
