# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.core import serializers
from django.test import TestCase

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.utils import get_content_type
from tests.utils import TestCaseMixins

USER_MODEL = get_user_model()


class JSONFieldTestCase(TestCase, TestCaseMixins):

    def test_field_is_json_serializable(self):
        instance = AccessRule.objects.create(ctype_source=get_content_type(USER_MODEL),
                                             ctype_target=get_content_type(USER_MODEL),
                                             relation_types=[
                                                 {'GROUPS': None}
                                             ])
        json = serializers.serialize('json', [instance])
        self.assertIsJSON(json)

