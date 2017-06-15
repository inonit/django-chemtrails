# -*- coding: utf-8 -*-

from collections import defaultdict, OrderedDict

from django.test import TestCase

from chemtrails.contrib.permissions.forms import JSONField
# from tests.testapp.models import JSONModel
#
#
# class JSONFieldTestCase(TestCase):
#
#     model = JSONModel
#     field = JSONField
#
#     def test_null_true_default(self):
#         field = self.field(null=True)
#         self.assertEqual(field.get_default(), None)
#
#     def test_null_false_default(self):
#         field = self.field(null=False)
#         self.assertEqual(field.get_default(), defaultdict(OrderedDict))
