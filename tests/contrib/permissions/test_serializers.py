# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.test import TestCase
from rest_framework import serializers

from chemtrails.contrib.permissions.serializers import ContentTypeIdentityField


class ContentTypeIdentityFieldTestCase(TestCase):

    def setUp(self):

        class TestSerializer(serializers.Serializer):
            ctype = ContentTypeIdentityField(queryset=ContentType.objects.all())

        self.Serializer = TestSerializer
        self.ctype = ContentType.objects.get(app_label='auth', model='user')

    def test_serialize_read(self):
        serializer = self.Serializer(data={'ctype': 'auth.user'})
        self.assertTrue(serializer.is_valid())
        self.assertEqual(serializer.validated_data['ctype'], self.ctype)

