# -*- coding: utf-8 -*-

from collections import defaultdict

from neomodel import db
from chemtrails.utils import flatten


def get_relationship_types():
    """
    :returns: A flat list of all relationship types in the database.
    :rtype: list
    """
    query = 'MATCH (n)-[r]-() RETURN DISTINCT type(r) ORDER BY (type(r))'
    result, _ = db.cypher_query(query)
    return list(flatten(result))


def get_node_relationship_types(params=None):
    """
    :param: params: Optional node filtering parameters.
    :returns: Dictionary with node label and relationship types.
    :rtype: dict[list]
    """
    mapping = defaultdict(list)
    query = ' '.join(('MATCH (n)-[r]-()',
                      'WHERE' if params else '',
                      ' AND '.join(['n.{} = {{{}}}'.format(key, key) for key in params.keys()]) if params else '',
                      'RETURN DISTINCT labels(n), type(r)'))
    result, _ = db.cypher_query(query, params)
    for label, relationship_type in result:
        label = label[0]
        mapping[label].append(relationship_type)
    return mapping
