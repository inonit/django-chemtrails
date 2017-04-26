# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework.permissions import DjangoObjectPermissions

from rest_framework.serializers import ModelSerializer
from rest_framework import status
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ModelViewSet

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.rest_framework.filters import ChemoPermissionsFilter
from tests.testapp.autofixtures import Book, BookFixture

User = get_user_model()
factory = APIRequestFactory()


class ChemoPermissionsFilterTestCase(TestCase):

    def setUp(self):
        # Create two separate graphs, each with a single book,
        # one publisher, two authors and two user objects.
        BookFixture(Book, generate_m2m={'authors': (2, 2)}).create(2)

        class BookSerializer(ModelSerializer):
            class Meta:
                model = Book
                fields = '__all__'

        class BookViewSet(ModelViewSet):
            queryset = Book.objects.all()
            serializer_class = BookSerializer
            permission_classes = [DjangoObjectPermissions]
            filter_backends = [ChemoPermissionsFilter]

        self.book_view = BookViewSet

    def test_filter_get_objects_for_user(self):
        user = User.objects.latest('pk')

        permission = Permission.objects.get(codename='view_book')
        user.user_permissions.add(permission)

        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_by_natural_key('auth', 'user'),
            ctype_target=ContentType.objects.get_by_natural_key('testapp', 'book'),
            is_active=True,
            relation_types=['AUTHOR', 'BOOK']
        )
        access_rule.permissions.add(permission)

        request = factory.get(path='/', data='', content_type='application/json')
        force_authenticate(request, user)
        response = self.book_view.as_view(actions={'get': 'list'})(request)

        # Make sure we can't reach any nodes living in the "other"
        # graph.
        self.assertEqual(len(response.data), 1)
