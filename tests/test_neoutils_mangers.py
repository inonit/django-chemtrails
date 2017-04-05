# -*- coding: utf-8 -*-

from django.test import TestCase

from neomodel import db

from chemtrails.neoutils import get_node_for_object
from chemtrails.neoutils.managers import PathManager

from tests.testapp.autofixtures import Book, BookFixture
from tests.utils import flush_nodes


class PathManagerTestCase(TestCase):

    def setUp(self):
        self.node = get_node_for_object(BookFixture(Book).create_one())

    @flush_nodes()
    def tearDown(self):
        pass

    def test_node_has_path_manager(self):
        self.assertIsInstance(self.node.paths, PathManager)

    def test_path_manager_add_relationship(self):
        query = self.node.paths.add('AUTHORS').add('USER').get_path_statement()
        try:
            result, meta = db.cypher_query(query)
        except Exception as e:
            raise e
        self.assertEqual(True, True)
