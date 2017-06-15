# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import QuerySet
from django.test import TestCase

from chemtrails.contrib.permissions import utils
from chemtrails.contrib.permissions.exceptions import MixedContentTypeError
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.neoutils import get_node_for_object, get_nodeset_for_queryset
from tests.testapp.autofixtures import Author, AuthorFixture, Book, BookFixture, Store, StoreFixture
from tests.utils import flush_nodes, clear_neo4j_model_nodes

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

    @flush_nodes()
    def test_get_identity_user(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        self.assertEqual(utils.get_identity(user), (user, None))

    @flush_nodes()
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

    @flush_nodes()
    def test_get_content_type_from_instance(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        self.assertEqual(utils.get_content_type(user),
                         ContentType.objects.get_for_model(User))


class CheckPermissionsAppLabelTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.check_permissions_app_label()``.
    """
    @flush_nodes()
    def test_check_permissions_app_label_single(self):
        perm = 'testapp.add_book'
        book = BookFixture(Book).create_one()
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(book), {'add_book'}))
        self.assertEqual(utils.check_permissions_app_label(perm),
                         (utils.get_content_type(Book), {'add_book'}))

    @flush_nodes()
    def test_check_permissions_app_label_invalid_fails(self):
        perm = 'testapp.invalid_permission'
        self.assertRaisesMessage(
            ContentType.DoesNotExist, 'ContentType matching query does not exist.',
            utils.check_permissions_app_label, permissions=perm)

    @flush_nodes()
    def test_check_permissions_app_label_sequence(self):
        perms = ['testapp.add_book', 'testapp.change_book']
        book = BookFixture(Book).create_one()

        ctype, codenames = utils.check_permissions_app_label(perms)
        self.assertEqual(ctype, utils.get_content_type(book))
        self.assertEqual(sorted(codenames), ['add_book', 'change_book'])

    def test_check_permissions_app_label_sequence_fails(self):
        perms = ['testapp.add_book', 'auth.add_user']
        self.assertRaisesMessage(
            MixedContentTypeError, ('Given permissions must have the same app label '
                                    '(testapp != auth).'),
            utils.check_permissions_app_label, permissions=perms)

        perms = ['testapp.add_book', 'testapp.add_store']
        self.assertRaisesMessage(
            MixedContentTypeError, ('Calculated content type from permission "testapp.add_store" '
                                    'store does not match <ContentType: book>.'),
            utils.check_permissions_app_label, permissions=perms)


class GetObjectsForUserTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.get_objects_for_user()``.
    """

    def setUp(self):
        clear_neo4j_model_nodes()

        BookFixture(Book, generate_m2m={'authors': (2, 2)}).create_one()
        self.user1, self.user2 = User.objects.earliest('pk'), User.objects.latest('pk')
        self.group = Group.objects.create(name='group')

    def tearDown(self):
        clear_neo4j_model_nodes()

    def test_superuser(self):
        self.user1.is_superuser = True
        queryset = Book.objects.all()
        objects = utils.get_objects_for_user(self.user1, ['testapp.change_book'], queryset)
        self.assertEqual(set(queryset), set(objects))

    def test_with_superuser_true(self):
        self.user1.is_superuser = True
        queryset = Book.objects.all()
        objects = utils.get_objects_for_user(self.user1,
                                             ['testapp.change_book'], queryset, with_superuser=True)
        self.assertEqual(set(queryset), set(objects))

    def test_with_superuser_false(self):
        BookFixture(Book, follow_fk=True, generate_m2m={'authors': (1, 1)}).create(count=2)

        user = User.objects.latest('pk')
        user.is_superuser = True

        # `with_superuser=False` requires defined access rules - should yield no results!
        self.assertEqual(set(Book.objects.none()),
                         set(utils.get_objects_for_user(
                             user, ['testapp.change_book'], Book.objects.all(), with_superuser=False)))

        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(user),
                                                ctype_target=utils.get_content_type(Book),
                                                relation_types=[
                                                    {'AUTHOR': None},
                                                    {'BOOK': None}
                                                ])
        perm = Permission.objects.get(content_type__app_label='testapp', codename='change_book')
        access_rule.permissions.add(perm)
        user.user_permissions.add(perm)

        objects = utils.get_objects_for_user(user,
                                             ['testapp.change_book'], Book.objects.all(), with_superuser=False)
        self.assertEqual(set(user.author.book_set.all()), set(objects))

    def test_anonymous(self):
        user = AnonymousUser()
        queryset = Book.objects.all()
        objects = utils.get_objects_for_user(user,
                                             ['testapp.change_book'], queryset)
        self.assertEqual(set(Book.objects.none()), set(objects))

    def test_nonexistent_source_node(self):
        user = User.objects.create_user(username='testuser')

        node = get_node_for_object(user).sync()
        node.delete()

        objects = utils.get_objects_for_user(user, ['testapp.add_book'])
        self.assertEqual(set(objects), set(Book.objects.none()))

    def test_mixed_permissions(self):
        codenames = [
            'testapp.change_book',
            'testapp.change_store'
        ]
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user, self.user1, codenames)

    def test_mixed_app_label_permissions(self):
        codenames = [
            'testapp.change_book',
            'auth.change_user'
        ]
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user, self.user1, codenames)

    def test_mixed_ctypes_no_klass(self):
        codenames = [
            'testapp.change_book',
            'auth.change_user'
        ]
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user, self.user1, codenames)

    def test_mixed_ctypes_with_klass(self):
        codenames = [
            'testapp.change_book',
            'auth.change_user'
        ]
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user, self.user1, codenames, Book)

    def test_no_app_label_or_klass(self):
        self.assertRaises(ValueError, utils.get_objects_for_user, self.user1, ['change_book'])

    def test_empty_permissions_sequence(self):
        objects = utils.get_objects_for_user(self.user1, [], Book.objects.all())
        self.assertEqual(set(objects), set())

    def test_permissions_single(self):
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(perm)
        self.user1.user_permissions.add(perm)

        self.assertEqual(
            set(utils.get_objects_for_user(self.user1, 'auth.change_group')),
            set(utils.get_objects_for_user(self.user1, ['auth.change_group']))
        )

    def test_klass_as_model(self):
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(perm)
        self.user1.user_permissions.add(perm)

        self.user1.groups.add(self.group)

        objects = utils.get_objects_for_user(self.user1,
                                             ['auth.change_group'], Group)
        self.assertEqual([obj.name for obj in objects], [self.group.name])

    def test_klass_as_manager(self):
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(perm)
        self.user1.user_permissions.add(perm)

        self.user1.groups.add(self.group)

        objects = utils.get_objects_for_user(self.user1,
                                             ['auth.change_group'], Group.objects)
        self.assertEqual([obj.name for obj in objects], [self.group.name])

    def test_klass_as_queryset(self):
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(perm)
        self.user1.user_permissions.add(perm)

        self.user1.groups.add(self.group)

        objects = utils.get_objects_for_user(self.user1,
                                             ['auth.change_group'], Group.objects.all())
        self.assertEqual([obj.name for obj in objects], [self.group.name])

    def test_ensure_returns_queryset(self):
        objects = utils.get_objects_for_user(self.user1, ['auth.change_group'])
        self.assertTrue(isinstance(objects, QuerySet))
        self.assertEqual(objects.model, Group)

    def test_single_permission_to_check(self):
        groups = Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2', 'group3']])
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(perm)
        self.user1.user_permissions.add(perm)

        self.user1.groups.add(*groups)

        objects = utils.get_objects_for_user(self.user1, 'auth.change_group')
        self.assertEqual(len(groups), len(objects))
        self.assertEqual(set(groups), set(objects))

    def test_multiple_permissions_to_check(self):
        groups = Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2', 'group3']])
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        add_perm = Permission.objects.get(content_type__app_label='auth', codename='add_group')
        change_perm = Permission.objects.get(content_type__app_label='auth', codename='change_group')
        access_rule.permissions.add(*[add_perm, change_perm])
        self.user1.user_permissions.add(*[add_perm, change_perm])

        self.user1.groups.add(*groups)
        objects = utils.get_objects_for_user(self.user1, ['auth.add_group', 'auth.change_group'])

        self.assertEqual(len(groups), len(objects))
        self.assertEqual(set(groups), set(objects))

    def test_multiple_permissions_to_check_requires_staff(self):
        groups = Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2', 'group3']])
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                requires_staff=True,
                                                relation_types=[{'GROUPS': None}])
        perms = Permission.objects.filter(content_type__app_label='auth', codename__in=['add_group', 'delete_group'])
        access_rule.permissions.add(*perms)

        self.user1.user_permissions.add(*perms)
        self.user1.groups.add(*groups)

        self.user1.is_staff = True
        get_node_for_object(self.user1).sync()  # Sync node in order to write `is_staff` property

        objects = utils.get_objects_for_user(self.user1, ['auth.add_group', 'auth.delete_group'])
        self.assertEqual(set(groups), set(objects))

        self.user2.user_permissions.add(*perms)
        self.user2.groups.add(*groups)

        self.assertFalse(self.user2.is_staff)

        objects = utils.get_objects_for_user(self.user2, ['auth.add_group', 'auth.delete_group'])
        self.assertEqual(set(), set(objects))

    def test_multiple_permissions_to_check_use_groups(self):
        self.group.permissions.add(Permission.objects.get(content_type__app_label='auth', codename='add_group'))
        self.user1.user_permissions.add(Permission.objects.get(content_type__app_label='auth', codename='change_group'))

        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        access_rule.permissions.add(*Permission.objects.filter(content_type__app_label='auth',
                                                               codename__in=['add_group', 'change_group']))

        self.user1.groups.add(self.group)
        objects = utils.get_objects_for_user(self.user1,
                                             ['auth.add_group', 'auth.change_group'], use_groups=True)
        self.assertEqual(set(self.user1.groups.all()), set(objects))

        self.user1.groups.remove(self.group)
        objects = utils.get_objects_for_user(self.user1,
                                             ['auth.add_group', 'auth.change_group'], use_groups=False)
        self.assertEqual(set(), set(objects))

    def test_extra_perms_single(self):
        group = Group.objects.create(name='a group')
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        access_rule.permissions.add(Permission.objects.get(content_type__app_label='auth', codename='add_group'))
        self.user1.groups.add(group)

        objects = utils.get_objects_for_user(self.user1, 'auth.add_group')
        self.assertEqual(set(), set(objects))

        objects = utils.get_objects_for_user(self.user1, 'auth.add_group', extra_perms='auth.add_group')
        self.assertEqual({group}, set(objects))

    def test_extra_perms_sequence(self):
        group = Group.objects.create(name='a group')
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        access_rule.permissions.add(*Permission.objects.filter(content_type__app_label='auth',
                                                               codename__in=['add_group', 'change_group']))
        self.user1.groups.add(group)

        objects = utils.get_objects_for_user(self.user1, 'auth.add_group')
        self.assertEqual(set(), set(objects))

        objects = utils.get_objects_for_user(self.user1, 'auth.add_group',
                                             extra_perms=['auth.add_group', 'auth.change_group'])
        self.assertEqual({group}, set(objects))

    def test_extra_perms_single_mixed_ctype(self):
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user,
                          self.user1, 'auth.add_user', extra_perms='testapp.change_store')

    def test_extra_perms_sequence_mixed_ctype(self):
        codenames = [
            'testapp.change_book',
            'testapp.change_store'
        ]
        self.assertRaises(MixedContentTypeError, utils.get_objects_for_user,
                          self.user1, 'auth.add_user', extra_perms=codenames)

    def test_any_permissions(self):
        groups = Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2', 'group3']])
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': None}])
        perms = Permission.objects.filter(content_type__app_label='auth', codename__in=['add_group', 'change_group'])
        access_rule.permissions.add(*perms)

        self.user1.user_permissions.add(*perms)
        self.user1.groups.add(*groups)

        objects = utils.get_objects_for_user(self.user1, ['auth.add_group', 'auth.delete_group'], any_perm=False)
        self.assertEqual(set(), set(objects))

        objects = utils.get_objects_for_user(self.user1, ['auth.add_group', 'auth.delete_group'], any_perm=True)
        self.assertEqual(set(groups), set(objects))

    def test_relation_types_target_props(self):
        groups = Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2']])
        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(Group),
                                                relation_types=[{'GROUPS': {'name': 'group1'}}])
        perm = Permission.objects.get(content_type__app_label='auth', codename='add_group')
        access_rule.permissions.add(perm)

        self.user1.user_permissions.add(perm)
        self.user1.groups.add(*groups)

        objects = utils.get_objects_for_user(self.user1, 'auth.add_group')
        self.assertEqual({Group.objects.get(name='group1')}, set(objects))

    def test_relation_types_definition_source_variable(self):
        book = BookFixture(Book, generate_m2m={'authors': (2, 2)}).create_one()
        get_nodeset_for_queryset(Store.objects.filter(pk=book.pk), sync=True)

        user = User.objects.filter(pk__in=book.authors.values('user')).latest('pk')
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_user')

        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(User),
                                                relation_types=[
                                                    {'AUTHOR': None},
                                                    {'BOOK': None},
                                                    {'AUTHORS': None},
                                                    {'USER': {
                                                        'pk': '{source}.pk',
                                                        'username': '{source}.username'
                                                    }}
                                                ])
        access_rule.permissions.add(perm)
        user.user_permissions.add(perm)

        objects = utils.get_objects_for_user(user, 'auth.change_user')
        self.assertEqual({user}, set(objects))
        self.assertNotEqual(User.objects.count(), objects.count())

    def test_relation_types_definition_index_variable(self):
        book = BookFixture(Book, generate_m2m={'authors': (2, 2)}).create_one()
        get_nodeset_for_queryset(Store.objects.filter(pk=book.pk), sync=True)

        user = User.objects.filter(pk__in=book.authors.values('user')).latest('pk')
        perm = Permission.objects.get(content_type__app_label='auth', codename='change_user')

        access_rule = AccessRule.objects.create(ctype_source=utils.get_content_type(User),
                                                ctype_target=utils.get_content_type(User),
                                                relation_types=[
                                                    {'AUTHOR': None},
                                                    {'BOOK': None},
                                                    {'{0:AUTHORS}': None},
                                                    {'USER': None}
                                                ])
        access_rule.permissions.add(perm)
        user.user_permissions.add(perm)

        objects = utils.get_objects_for_user(user, 'auth.change_user')
        self.assertEqual({user}, set(objects))
        self.assertNotEqual(User.objects.count(), objects.count())


class GetObjectsForGroupTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.get_objects_for_group()``.
    """
    pass


class GraphPermissionCheckerTestCase(TestCase):
    """
    Testing ``chemtrails.contrib.permissions.utils.GraphPermissionChecker`` class.
    """
    @flush_nodes()
    def test_checker_has_perm_inactive_user(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_active=False)
        checker = utils.GraphPermissionChecker(user)
        self.assertFalse(checker.has_perm(perm=None, obj=None))

    @flush_nodes()
    def test_checker_has_perm_is_superuser(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_superuser=True)
        checker = utils.GraphPermissionChecker(user)
        self.assertTrue(checker.has_perm(perm=None, obj=None))

    @flush_nodes()
    def test_get_user_filters(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        # Get user filters for user
        checker = utils.GraphPermissionChecker(user)
        filters = checker.get_user_filters()
        permissions = Permission.objects.filter(**filters)
        self.assertIsInstance(permissions, QuerySet)
        self.assertEqual(permissions.count(), 2)

    @flush_nodes()
    def test_get_user_perms(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(list(checker.get_user_perms(user))), ['add_user', 'change_user'])

    @flush_nodes()
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

    @flush_nodes()
    def test_get_group_perms(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(*Permission.objects.filter(codename__in=['add_user', 'change_user']))

        user = User.objects.create_user(username='testuser', password='test123.')

        checker = utils.GraphPermissionChecker(group)
        self.assertListEqual(sorted(list(checker.get_group_perms(user))), ['add_user', 'change_user'])

    @flush_nodes()
    def test_get_perms_user_is_inactive(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_active=False)
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(checker.get_perms(user), [])

    def test_get_perms_user_is_superuser(self):
        user = User.objects.create_user(username='testuser', password='test123.', is_superuser=True)
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(checker.get_perms(user)), ['add_user', 'change_user', 'delete_user'])

    @flush_nodes()
    def test_get_perms_user_in_group(self):
        group = Group.objects.create(name='test group')
        group.permissions.add(Permission.objects.get(codename='add_user'))

        user = User.objects.create_user(username='testuser', password='test123.')
        user.user_permissions.add(Permission.objects.get(codename='change_user'))
        user.groups.add(group)

        # Make sure we get user and group permissions combined
        checker = utils.GraphPermissionChecker(user)
        self.assertListEqual(sorted(checker.get_perms(user)), ['add_user', 'change_user'])

    @flush_nodes()
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
                                                relation_types=[{'AUTHOR': None}])
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
                                                relation_types=[{'USER_SET': None}])
        user.groups.add(group)
        group.permissions.add(perm)
        access_rule.permissions.add(perm)

        checker = utils.GraphPermissionChecker(group)
        # self.assertTrue(checker.has_perm(perm.codename, user))
        self.assertRaises(NotImplementedError, checker.has_perm, perm.codename, user)
