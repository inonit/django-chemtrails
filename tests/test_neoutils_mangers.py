# -*- coding: utf-8 -*-

from django.test import TestCase

from neomodel import db

from chemtrails.neoutils import get_node_for_object
from chemtrails.neoutils.managers import PathManager

from tests.testapp.autofixtures import get_user_model, Book, BookFixture
from tests.utils import flush_nodes


class PathManagerTestCase(TestCase):

    def setUp(self):
        self.node = get_node_for_object(BookFixture(Book).create_one())

    @flush_nodes()
    def tearDown(self):
        pass

    def test_node_has_path_manager(self):
        self.assertIsInstance(self.node.paths, PathManager)

    def test_path_manager_build_path_query(self):
        user = get_user_model().objects.latest('pk')
        query = self.node.paths.add('AUTHORS').add('USER', target_props={
            'pk': user.pk,
            'username': user.username,
            'is_active': user.is_active
        }).get_path()
        result, meta = db.cypher_query(query)
        self.assertTrue(len(result))
        self.assertEqual(meta, ('path',))

    def test_path_manager_build_match_query(self):
        query = self.node.paths.add('AUTHORS').add('USER').get_match()
        result, meta = db.cypher_query(query)
        self.assertTrue(len(result))
