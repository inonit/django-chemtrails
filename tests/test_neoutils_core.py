# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import six

from neomodel import *
from neomodel.match import NodeSet

from chemtrails.neoutils import (
    ModelNodeMeta, ModelNodeMixin, MetaNodeMeta, MetaNodeMixin,
    get_meta_node_class_for_model, get_node_class_for_model,
    get_node_for_object, get_nodeset_for_queryset
)

from tests.testapp.autofixtures import BookFixture, StoreFixture
from tests.testapp.models import Book, Store


class NodeUtilsTestCase(TestCase):
    """
    Test various utility functions for dealing with
    model and node instances.
    """
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

    def test_get_nodeset_for_queryset(self):
        queryset = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                   StoreFixture(Store).create(count=3, commit=True)))
        nodeset = get_nodeset_for_queryset(queryset)
        self.assertIsInstance(nodeset, NodeSet)
        for node in nodeset:
            self.assertIsInstance(node, get_node_class_for_model(queryset.model))


class ModelNodeTestCase(TestCase):

    def test_create_model_node(self):
        book = BookFixture(Book).create_one()

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            class Meta:
                model = Book

        self.assertTrue(issubclass(ModelNode, StructuredNode))
        self.assertIsInstance(ModelNode(instance=book), StructuredNode)

    def test_create_model_node_declaring_model_in_class(self):
        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            __metaclass_model__ = Book
            class Meta:
                model = None

        self.assertEqual(ModelNode.Meta.model, Book)

    def test_create_model_node_custom_app_label(self):
        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            class Meta:
                model = Book
                app_label = 'custom_app_label'

        self.assertEqual(ModelNode.Meta.app_label, 'custom_app_label')

    def test_create_model_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(ModelNodeMeta)
            class ModelNode(ModelNodeMixin, StructuredNode):
                class Meta:
                    model = None

            self.fail('Did not fail when defining a ModelNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'ModelNode')

    def test_create_model_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(ModelNodeMeta)
            class ModelNode(ModelNodeMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a ModelNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'ModelNode')


class MetaNodeTestCase(TestCase):

    def test_create_meta_node(self):
        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            class Meta:
                model = Book

        self.assertTrue(issubclass(MetaNode, StructuredNode))
        self.assertIsInstance(MetaNode(), StructuredNode)

    def test_create_meta_node_declaring_model_in_class(self):
        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            __metaclass_model__ = Book
            class Meta:
                model = None

        self.assertEqual(MetaNode.Meta.model, Book)

    def test_create_meta_node_custom_app_label(self):
        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            class Meta:
                model = Book
                app_label = 'custom_app_label'

        self.assertEqual(MetaNode.Meta.app_label, 'custom_app_label')

    def test_create_meta_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class MetaNode(MetaNodeMixin, StructuredNode):
                class Meta:
                    model = None

            self.fail('Did not fail when defining a MetaNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'MetaNode')

    def test_create_meta_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class MetaNode(MetaNodeMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a MetaNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'MetaNode')
