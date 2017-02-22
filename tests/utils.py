# -*- coding: utf-8 -*-

from django.test import TestCase

from contextlib import ContextDecorator
from neomodel import db


def clear_neo4j_model_nodes():
    db.cypher_query("MATCH (n) WHERE n.type = 'ModelNode' DETACH DELETE n")


class flush_nodes(ContextDecorator):
    """
    Context decorator which will wipe out the all
    ``ModelNode`` nodes on enter and exit.
    """

    def __enter__(self):
        clear_neo4j_model_nodes()

    def __exit__(self, *exc):
        clear_neo4j_model_nodes()


class ChemtrailsTestCase(TestCase):
    """
    Deletes all ``ModelNodes`` from Neo4j in setUp() and tearDown().
    ``MetaNodes`` are created during migration, and are left intact.
    """

    def setUp(self):
        super(ChemtrailsTestCase, self).setUp()
        clear_neo4j_model_nodes()

    def tearDown(self):
        super(ChemtrailsTestCase, self).tearDown()
        clear_neo4j_model_nodes()
