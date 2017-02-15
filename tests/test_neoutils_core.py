# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import six

from neomodel import *

from chemtrails.neoutils import MetaNodeMeta, MetaNodeMixin
from chemtrails.neoutils import get_meta_node_class_for_model, get_node_class_for_model, get_node_for_object

from tests.testapp.autofixtures import StoreFixture
from tests.testapp.models import Book, Store


class ModelNodeUtilsTestCase(TestCase):

    def test_get_relations_node_class_for_model(self):
        klass = get_meta_node_class_for_model(Book)
        self.assertTrue(issubclass(klass, StructuredNode))

    def test_get_node_class_for_model(self):
        klass = get_node_class_for_model(Book)
        self.assertTrue(issubclass(klass, StructuredNode))

    def test_get_node_for_object(self):
        store = StoreFixture(Store).create_one(commit=True)
        store_node = get_node_for_object(store)
        self.assertIsInstance(store_node, get_node_class_for_model(Store))

    def test_get_node_for_multiple_objects(self):
        stores = StoreFixture(Store).create(count=3, commit=True)
        for store in stores:
            store_node = get_node_for_object(store).sync()
            self.assertIsInstance(store_node, get_node_class_for_model(Store))


class ModelRelationsNodeTestCase(TestCase):

    def test_create_node(self):
        @six.add_metaclass(MetaNodeMeta)
        class RelationNode(MetaNodeMixin, StructuredNode):
            class Meta:
                model = Book
                app_label = 'test'

        self.assertIsInstance(RelationNode(), StructuredNode)

    def test_create_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class RelationNode(MetaNodeMixin, StructuredNode):
                class Meta:
                    model = None

            self.fail('Did not fail when defining a ModelRelationNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'RelationNode')

    def test_create_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class RelationNode(MetaNodeMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a ModelRelationNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'RelationNode')
