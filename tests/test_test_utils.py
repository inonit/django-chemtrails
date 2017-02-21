# -*- coding: utf-8 -*-

from django.test import TestCase

from neomodel import StructuredNode
from chemtrails.neoutils import get_node_for_object, get_node_class_for_model

from tests.utils import flush_nodes
from tests.testapp.autofixtures import BookFixture
from tests.testapp.models import Book


class FlushNodesTestCase(TestCase):
    """
    Make sure the flush_nodes context decorator is working.
    """

    def test_flush_nodes_context_manager(self):

        with flush_nodes():
            book = BookFixture(Book).create_one()

            node = get_node_for_object(book)
            self.assertIsInstance(node, StructuredNode)

            klass = get_node_class_for_model(Book)
            self.assertEqual(len(klass.nodes.all()), 1)

        self.assertEqual(len(klass.nodes.all()), 0)

    def test_flush_nodes_context_decorator(self):

        @flush_nodes()
        def create_nodes():
            book = BookFixture(Book).create_one()

            node = get_node_for_object(book)
            assert isinstance(node, StructuredNode)

            klass = get_node_class_for_model(Book)
            assert len(klass.nodes.all()) == 1

        create_nodes()

        klass = get_node_class_for_model(Book)
        self.assertEqual(len(klass.nodes.all()), 0)

