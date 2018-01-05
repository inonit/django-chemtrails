# -*- coding: utf-8 -*-

from collections import defaultdict

from django.core.exceptions import ValidationError

from libcypher_parser import parse_statement
from neomodel import db
from chemtrails.utils import flatten


def get_relationship_types():
    """
    :returns: A flat list of all relationship types in the database.
    :rtype: list
    """
    query = 'MATCH (n)-[r]-() RETURN DISTINCT type(r) ORDER BY (type(r))'
    validate_cypher(query, raise_exception=True)
    result, _ = cypher_query(db, query)
    return list(flatten(result))


def get_node_permissions():
    """
    :returns: A distinct list of all available permissions.
    :rtype: list
    """
    query = 'MATCH (n)-[r]-() WHERE n.type = \'MetaNode\' RETURN DISTINCT n.default_permissions'
    validate_cypher(query, raise_exception=True)
    result, _ = cypher_query(db, query)
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
    validate_cypher(query, raise_exception=True)
    result, _ = cypher_query(db, query, params)
    for label, relationship_type in result:
        label = label[0]
        mapping[label].append(relationship_type)
    return mapping


def validate_cypher(statement, raise_exception=False, exc_class=ValidationError):
    """
    Checks if ``statement`` is a valid Cypher statement.
    
    :param statement: Cypher statement to parse.
    :type statement: str
    :param raise_exception: Raise ValidationError if not valid.
    :type raise_exception: bool
    :param exc_class: Exception class to raise
    :type exc_class: Class
    """
    is_valid, data = parse_statement(statement)
    if not is_valid and raise_exception:
        raise exc_class('Failed to validate Cypher statement', params=data)
    return is_valid, data


def cypher_query(db, query, params=None, query_type='read', **kwargs):
    """Takes a read query and runs it in a read only or write context.

    neo4j-driver doesn't know how to evaluate whether a query is
    a read or a write query. In a sense it can't tell the difference
    between a MATCH or a MERGE query.

    This is a candy function you can use for known read-only queries,
    to enable them to scale better.

    Takes a neomodel database (db) object and a cypher query as parameters,
    along with a query type of string 'read' or 'write'.

    Defaults to the safer value 'read'
    """
    def db_cypher_query_wrapper(tx, db, query, params=None, **kwargs):
        """Wrap db.cypher_query taking into account transaction type"""

        # The need to set an internal transaction in db
        # is that db.cypher_query returns more than a statementresult.
        return db.cypher_query(query, params, tx=tx, **kwargs)

    with db.driver.session() as session:
        if query_type == 'read':
            return session.read_transaction(db_cypher_query_wrapper, db, query, params=params, **kwargs)
        elif query_type == 'write':
            return session.write_transaction(db_cypher_query_wrapper, db, query, params=params, **kwargs)
        else:
            raise ValueError('Unknown query type. Must be "read" or "write"')
