# -*- coding: utf-8 -*-

from contextlib import ContextDecorator
from neomodel import db


class flush_nodes(ContextDecorator):
    """
    Context decorator which will wipe out the all
    ``ModelNode`` nodes.
    """

    def __enter__(self):
        pass

    def __exit__(self, *exc):
        db.cypher_query("MATCH (n) WHERE n.type = 'ModelNode' DETACH DELETE n")
