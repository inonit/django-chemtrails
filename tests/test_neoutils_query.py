# -*- coding: utf-8 -*-

from django.core.exceptions import ValidationError
from django.test import TestCase

from chemtrails.neoutils import query


class QueryFunctionsTestCase(TestCase):
    """
    Test the various query functions in chemtrails.neoutils.query.
    """

    def test_get_relationship_types(self):
        expected = ['ACCESSRULE', 'ACCESSRULE_CTYPE_SOURCE_SET', 'ACCESSRULE_CTYPE_TARGET_SET', 'ACCESSRULE_PERMISSIONS',
                    'AUTHOR', 'AUTHORS', 'BESTSELLER', 'BESTSELLER_STORES', 'BOOK', 'BOOKS', 'CONTACT', 'CONTENT_TYPE',
                    'CONTENT_TYPE_SET_FOR_TAG', 'CTYPE_SOURCE', 'CTYPE_TARGET', 'GROUP', 'GROUPS', 'GUILD',
                    'GUILDS', 'GUILD_CONTACTS', 'GUILD_SET', 'MEMBERS',
                    'PERMISSION', 'PERMISSIONS', 'PUBLISHER', 'STORE', 'TAGS', 'USER', 'USER_PERMISSIONS', 'USER_SET']
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

    def test_validate_cypher_statement(self):
        is_valid, _ = query.validate_cypher('MATCH (n) RETURN n')
        self.assertTrue(is_valid)

        is_valid, _ = query.validate_cypher('MATCH RETURN n')
        self.assertFalse(is_valid)

        try:
            query.validate_cypher('Invalid cypher statement', raise_exception=True)
            self.fail('Did not raise ValidationError when validating invalid statement.')
        except ValidationError as e:
            self.assertEqual(str(e), "['Failed to validate Cypher statement']")
