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

    def test_test_get_node_relationship_types_with_params(self):
        params = {'type': 'MetaNode', 'app_label': 'auth'}
        result = query.get_node_relationship_types(params)
        self.assertIsInstance(result, dict)
        self.assertTrue(len(result), 6)
