# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.test import TestCase
from tests.testapp.models import OrderedJSONModel


class OrderedJSONFieldTestCase(TestCase):

    model = OrderedJSONModel

    def setUp(self):
        self.dict = {
            'alpha': True,
            'beta': {
                'romeo': 'juliet'
            },
            'gamma': 1
        }

    def test_field_create(self):
        obj1 = self.model.objects.create(json=self.dict)
        obj2 = self.model.objects.get(pk=obj1.pk)

        self.assertEqual(obj1.json, obj2.json)

    def test_modify_dict(self):
        obj = self.model.objects.create(json=self.dict)
        modified_dict = {
            'alpha': True,
            'new_key': 'something',
            'beta': {
                'romeo': 'juliet'
            },
            'gamma': 1,
            'foo': 'bar'
        }
        obj.json = modified_dict
        obj.save()

        self.assertEqual(obj.json, modified_dict)
