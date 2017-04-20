# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.test import TestCase

from chemtrails.contrib.permissions import utils
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.neoutils import get_nodeset_for_queryset
from tests.testapp.autofixtures import Author, AuthorFixture, Book, BookFixture, Store, StoreFixture
from tests.utils import flush_nodes

User = get_user_model()


class GetIdentityTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.get_identity()``.
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
    Testing ``chemtrails.contrib.permissions.utils.get_content_type()``.
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
    Testing ``chemtrails.contrib.permissions.utils.check_permissions_app_label()``.
    """

    def test_check_permissions_app_label_single(self):
        perm = 'testapp.add_book'
        book = BookFixture(Book).create_one()
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(book), {'add_book'}))
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(Book), {'add_book'}))

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
    Testing ``chemtrails.contrib.permissions.utils.get_objects_for_user()``.
    """

    @flush_nodes()
    def test_get_objects_for_user(self):
        permission = Permission.objects.get(codename='change_user')

        graph1 = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                 StoreFixture(Store).create(count=1, commit=True)))
        get_nodeset_for_queryset(graph1, sync=True, max_depth=1)
        graph1_user_pks = list(User.objects.values_list('pk', flat=True))

        graph2 = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                 StoreFixture(Store).create(count=1, commit=True)))
        get_nodeset_for_queryset(graph2, sync=True, max_depth=1)
        graph2_user_pks = list(User.objects.exclude(pk__in=graph1_user_pks).values_list('pk', flat=True))

        user1 = User.objects.get(pk=graph1_user_pks[0])
        user1.user_permissions.add(permission)

        user2 = User.objects.get(pk=graph2_user_pks[0])
        user2.user_permissions.add(permission)

        # Create an access rule from User to User following a path:
        # (UserNode)-[:AUTHOR]->(AuthorNode)-[:BOOK]->
        #   (BookNode)-[:STORE]->(StoreNode)-[:BOOKS]->
        #   (BookNode)-[:AUTHORS]->(AuthorNode)-[:USER]->(UserNode)
        rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                         ctype_target=utils.get_content_type(User),
                                         relation_types=[
                                             'AUTHOR', 'BOOK',
                                             'STORE', 'BOOKS',
                                             'AUTHORS', 'USER'
                                         ])
        rule.permissions.add(permission)

        # Check if a user in a graph can get a path to all other users in the same graph.
        permitted_objects = utils.get_objects_for_user(user=user1, permissions='auth.change_user')
        self.assertListEqual(graph1_user_pks, list(permitted_objects.values_list('pk', flat=True)))

        permitted_objects = utils.get_objects_for_user(user=user1, permissions='auth.change_user',
                                                       klass=User.objects.all())
        self.assertListEqual(graph1_user_pks, list(permitted_objects.values_list('pk', flat=True)))

    @flush_nodes()
    def test_get_objects_for_user_is_superuser(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_superuser=True)
        BookFixture(Book, follow_fk=True, generate_m2m=False).create(count=5)
        self.assertListEqual(list(Book.objects.values_list('pk', flat=True)),
                             list(utils.get_objects_for_user(user=user, permissions='testapp.add_book')
                                  .values_list('pk', flat=True)))

    @flush_nodes()
    def test_get_objects_for_user_is_anonymous(self):
        user = AnonymousUser()
        BookFixture(Book, follow_fk=True, generate_m2m=False).create_one()
        self.assertListEqual(list(),
                             list(utils.get_objects_for_user(user=user, permissions='testapp.add_book')
                                  .values_list('pk', flat=True)))


class GetObjectsForGroupTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.get_objects_for_group()``.
    """
    pass


class GraphPermissionCheckerTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.GraphPermissionChecker`` class.
    """

    def test_checker_has_perm_inactive_user(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_active=False)
        checker = utils.GraphPermissionChecker(user)
        self.assertFalse(checker.has_perm(perm=None, obj=None))

    def test_checker_has_perm_is_superuser(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_superuser=True)
        checker = utils.GraphPermissionChecker(user)
        self.assertTrue(checker.has_perm(perm=None, obj=None))

    def test_get_user_filters(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        # Get user filters for user
        checker = utils.GraphPermissionChecker(user)
        filters = checker.get_user_filters()
        permissions = Permission.objects.filter(**filters)
        self.assertIsInstance(permissions, QuerySet)
        self.assertEqual(permissions.count(), 2)

    def test_get_user_perms(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(list(checker.get_user_perms(user))), ['add_user', 'change_user'])

    def test_get_group_filters(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        user = User.objects.create_user(username='testuser', password='test123.')
        user.groups.add(group)

        # Get group filters for group
        checker = utils.GraphPermissionChecker(group)
        filters = checker.get_group_filters()
        permissions = Permission.objects.filter(**filters)
        self.assertIsInstance(permissions, QuerySet)
        self.assertEqual(permissions.count(), 2)

        # Get group filters for use
        checker = utils.GraphPermissionChecker(user)
        filters = checker.get_group_filters()
        permissions = Permission.objects.filter(**filters)
        self.assertIsInstance(permissions, QuerySet)
        self.assertEqual(permissions.count(), 2)

    def test_get_group_perms(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        user = User.objects.create_user(username='testuser', password='test123.')

        checker = utils.GraphPermissionChecker(group)
        self.assertListEqual(sorted(list(checker.get_group_perms(user))), ['add_user', 'change_user'])

    def test_get_perms_user_is_inactive(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_active=False)
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(checker.get_perms(user), [])

    def test_get_perms_user_is_superuser(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_superuser=True)
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(checker.get_perms(user)), ['add_user', 'change_user', 'delete_user'])

    def test_get_perms_user_in_group(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(Permission.objects.get(codename='add_user'))

        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(Permission.objects.get(codename='change_user'))
        user.groups.add(group)

        # Make sure we get user and group permissions combined
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(checker.get_perms(user)), ['add_user', 'change_user'])

    def test_get_perms_group(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(Permission.objects.get(codename='add_group'))

        checker = utils.GraphPermissionChecker(group)
        self.assertListEqual(sorted(checker.get_perms(group)), ['add_group'])

    @flush_nodes()
    def test_checker_has_perm_authorized_user(self):
        author = AuthorFixture(Author).create_one()
        user = author.user
        perm = Permission.objects.get(content_type=utils.get_content_type(author), codename='change_author')
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(user),
                                                ctype_target=utils.get_content_type(author),
                                                relation_types=[
                                                    'AUTHOR'
                                                ])
        user.user_permissions.add(perm)
        access_rule.permissions.add(perm)

        checker = utils.GraphPermissionChecker(user)
        self.assertTrue(checker.has_perm(perm.codename, author))

    @flush_nodes()
    def test_checker_has_perm_authorized_group(self):
        group = Group.objects.create(name='test group')
        user = User.objects.create_user(username='testuser', password='test123.')
        perm = Permission.objects.get(content_type=utils.get_content_type(user), codename='change_user')
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(group),
                                                ctype_target=utils.get_content_type(user),
                                                relation_types=[
                                                    'USER_SET'
                                                ])
        user.groups.add(group)
        group.permissions.add(perm)
        access_rule.permissions.add(perm)

        checker = utils.GraphPermissionChecker(group)
        self.assertTrue(checker.has_perm(perm.codename, user))
