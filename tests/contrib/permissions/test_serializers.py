# -*- coding: utf-8 -*-

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from rest_framework import serializers
from chemtrails.contrib.permissions.serializers import (
    AccessRuleSerializer, ContentTypeIdentityField, PermissionIdentityField
)


class AccessRuleSerializerTestCase(TestCase):

    def test_access_rule_serializer_valid_data(self):
        serializer = AccessRuleSerializer(data={
            'ctype_source': 'auth.user',
            'ctype_target': 'testapp.book',
            'permissions': [
                'testapp.add_book',
                'testapp.change_book'
            ],
            'relation_types': [
                {'AUTHOR': None},
                {'BOOK': None}
            ]
        })
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.errors, {})

        self.assertEqual(serializer.validated_data['ctype_source'],
                         ContentType.objects.get(app_label='auth', model='user'))
        self.assertEqual(serializer.validated_data['ctype_target'],
                         ContentType.objects.get(app_label='testapp', model='book'))

        for perm in Permission.objects.filter(codename__in=['add_book', 'change_book']):
            self.assertTrue(perm in serializer.validated_data['permissions'])


class ContentTypeIdentityFieldTestCase(TestCase):

    def setUp(self):

        class TestSerializer(serializers.Serializer):
            ctype = ContentTypeIdentityField(queryset=ContentType.objects.all())

        self.Serializer = TestSerializer
        self.ctype = ContentType.objects.get(app_label='auth', model='user')

    def test_serialize_valid_input(self):
        serializer = self.Serializer(data={'ctype': 'auth.user'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['ctype'], self.ctype)

    def test_serialize_invalid_data_type(self):
        serializer = self.Serializer(data={'ctype': 1})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('ctype' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise ValidationError when serializing invalid data type using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(
                str(e), "{'ctype': ['Incorrect type. Expected content type string identifier, received int.']}")

    def test_serialize_invalid_length_content_type_string(self):
        serializer = self.Serializer(data={'ctype': 'auth'})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('ctype' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise ValidationError when serializing invalid content '
                      'type string using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(str(e), "{'ctype': ['Incorrect length. Expected content type string, "
                                     "separated by punctuation. Received \"auth\".']}")

    def test_serializer_non_existent_content_type(self):
        serializer = self.Serializer(data={'ctype': 'non.existent'})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('ctype' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise exception when serializing non-existent content '
                      'type string using using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(str(e), "{'ctype': ['Invalid content type \"non.existent\" - object does not exist.']}")


class PermissionIdentityFieldTestCase(TestCase):

    def setUp(self):

        class TestSerializer(serializers.Serializer):
            perm = PermissionIdentityField(queryset=Permission.objects.all())

        self.Serializer = TestSerializer
        self.ctype = ContentType.objects.get(app_label='auth', model='user')
        self.permission = Permission.objects.get(content_type=self.ctype, codename='add_user')
        self.perm_string = '{app_label}.{codename}'.format(app_label=self.ctype.app_label,
                                                           codename=self.permission.codename)

    def test_serialize_valid_permission_input(self):
        serializer = self.Serializer(data={'perm': self.perm_string})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['perm'], self.permission)

    def test_serialize_invalid_permission_data_type(self):
        serializer = self.Serializer(data={'perm': 1})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('perm' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise ValidationError when serializing invalid data type using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(
                str(e), "{'perm': ['Incorrect type. Expected permission string identifier, received int.']}")

    def test_serialize_invalid_length_permission_string(self):
        serializer = self.Serializer(data={'perm': 'add_user'})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('perm' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise ValidationError when serializing invalid permission '
                      'string using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(str(e), "{'perm': ['Incorrect length. Expected permission string identifier, "
                                     "separated by punctuation. Received \"add_user\".']}")

    def test_serializer_non_existent_permission(self):
        serializer = self.Serializer(data={'perm': 'auth.can_levitate'})
        self.assertFalse(serializer.is_valid())
        self.assertTrue('perm' in serializer.errors)

        try:
            serializer.is_valid(raise_exception=True)
            self.fail('Did not raise exception when serializing non-existent permission '
                      'string using using `raise_exception=True`')
        except serializers.ValidationError as e:
            self.assertEqual(str(e), "{'perm': ['Invalid permission \"auth.can_levitate\" "
                                     "- object does not exist.']}")
