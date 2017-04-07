# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from chemtrails.contrib.permissions import utils
from tests.testapp.autofixtures import Book, BookFixture

User = get_user_model()


class GetIdentityTestCase(TestCase):

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

    def test_get_content_type_from_class(self):
        self.assertEqual(utils.get_content_type(User),
                         ContentType.objects.get_for_model(User))

    def test_get_content_type_from_instance(self):
        user = User.objects.create_user(username='testuser', password='test123.')
        self.assertEqual(utils.get_content_type(user),
                         ContentType.objects.get_for_model(User))


class CheckPermissionsAppLabelTestCase(TestCase):

    def test_check_permissions_app_label_single(self):
        perm = 'testapp.add_book'
        book = BookFixture(Book).create_one()
        self.assertEqual(utils.check_permissions_app_label(perm, book),
                         (utils.get_content_type(book), ['add_book']))
        self.assertEqual(utils.check_permissions_app_label(perm, Book),
                         (utils.get_content_type(Book), ['add_book']))

    def test_check_permissions_app_label_single_fails(self):
        perm = 'testapp.add_store'
        book = BookFixture(Book).create_one()
        self.assertRaisesMessage(ValueError, '', utils.check_permissions_app_label, permissions=perm, klass=book)
        self.assertRaisesMessage(ValueError, '', utils.check_permissions_app_label, permissions=perm, klass=Book)

    def test_check_permissions_app_label_sequence(self):
        perms = ['testapp.add_book', 'testapp.change_book']
        book = BookFixture(Book).create_one()
        self.assertEqual(utils.check_permissions_app_label(perms, book),
                         (utils.get_content_type(book), ['change_book', 'add_book']))
        self.assertEqual(utils.check_permissions_app_label(perms, Book),
                         (utils.get_content_type(Book), ['change_book', 'add_book']))

    def test_check_permissions_app_label_sequence_fails(self):
        perms = ['testapp.add_book', 'testapp.add_store']
        book = BookFixture(Book).create_one()
        self.assertRaisesMessage(ValueError, '', utils.check_permissions_app_label, permissions=perms, klass=book)
        self.assertRaisesMessage(ValueError, '', utils.check_permissions_app_label, permissions=perms, klass=Book)
