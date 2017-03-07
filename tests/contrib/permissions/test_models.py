# -*- coding: utf-8 -*-

from django.test import TestCase

from chemtrails.contrib.permissions.models import get_node_relations_choices, get_node_permissions_choices


class ChoicesHelperFunctionsTestCase(TestCase):
    """
    Test various functions for getting choices based on Neo4j data.
    """

    def test_get_node_relations_choices(self):
        choices = get_node_relations_choices()

        self.assertIsInstance(choices, list)
        for item in choices:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)

    def test_get_node_permissions_choices(self):
        choices = get_node_permissions_choices()

        self.assertIsInstance(choices, list)
        for item in choices:
            self.assertIsInstance(item, tuple)
            self.assertEqual(len(item), 2)
