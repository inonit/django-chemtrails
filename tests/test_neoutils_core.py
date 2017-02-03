# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import six

from neomodel import *

from chemtrails.neoutils import ModelRelationsMeta, ModelRelationsMixin
from tests.testapp.models import Book


class ModelRelationsNodeTestCase(TestCase):

    def test_create_node(self):
        @six.add_metaclass(ModelRelationsMeta)
        class RelationNode(ModelRelationsMixin, StructuredNode):
            class Meta:
                model = Book

        self.assertIsInstance(RelationNode(), StructuredNode)

    def test_create_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(ModelRelationsMeta)
            class RelationNode(ModelRelationsMixin, StructuredNode):
                class Meta:
                    model = None

            self.fail('Did not fail when defining a ModelRelationNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'RelationNode')

    def test_create_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(ModelRelationsMeta)
            class RelationNode(ModelRelationsMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a ModelRelationNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'RelationNode')

