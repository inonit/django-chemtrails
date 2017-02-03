# -*- coding: utf-8 -*-

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase
from django.utils import six

from neomodel import *

from chemtrails.neoutils import ModelRelationsMeta, ModelRelationsMixin
from tests.testapp.models import Book


# class ModelRelationsNodeTestCase(TestCase):

    # def test_create_node_with_meta_class(self):
    #
    #     @six.add_metaclass(ModelRelationsMeta)
    #     class RelationNode(ModelRelationsMixin, StructuredNode):
    #         class Meta:
    #             model = Book
    #
    #     node = RelationNode().save()
    #
    #     self.assertIsInstance(RelationNode(), StructuredNode)

    # def test_create_node_fails_without_meta_class(self):
    #     try:
    #         class RelationNode(ModelRelationsNode):
    #             pass
    #         self.fail('Did not fail when defining a ModelRelationNode without a Meta class.')
    #     except ImproperlyConfigured as e:
    #         # FIXME: For some reason the exception is not caught here...
    #         self.assertEqual(str(e), '%s must implement a Meta class.' % 'ModelRelationsNode')
    #     pass

