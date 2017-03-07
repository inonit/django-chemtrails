# -*- coding: utf-8 -*-

from django.test import TestCase

from chemtrails.neoutils import query


class QueryFunctionsTestCase(TestCase):
    """
    Test the various query functions in chemtrails.neoutils.query.
    """

    def test_get_relationship_types(self):
        expected = ['AUTHOR', 'AUTHORS', 'BESTSELLER', 'BESTSELLER_STORES', 'BOOK', 'BOOKS', 'CONTENT_TYPE', 'GROUP',
                    'GROUPS', 'LOGENTRY', 'PERMISSION', 'PERMISSIONS', 'PUBLISHER', 'STORE', 'USER', 'USER_PERMISSIONS',
                    'USER_SET']
        self.assertEqual(expected, query.get_relationship_types())

    def test_get_node_relationship_types(self):
        result = query.get_node_relationship_types()
        self.assertIsInstance(result, dict)
        for key, val in result.items():
            self.assertIsInstance(key, str)
            self.assertIsInstance(val, list)

    def test_get_node_relationship_types_with_params(self):
        params = {'type': 'MetaNode', 'app_label': 'auth'}
        result = query.get_node_relationship_types(params)
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result), 6)

    def test_get_node_permissions(self):
        result = query.get_node_permissions()
        self.assertIsInstance(result, list)

    def test_shortest_path(self):
        from neomodel import db
        result, _ = db.cypher_query('MATCH (a:UserNode),(b:UserNode), p = allShortestPaths((a)-[*]-(b)) WHERE id(a) = 35 AND id(b) IN [47, 41, 37] RETURN p')

        for r in result:
            pass
