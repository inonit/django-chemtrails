# -*- coding: utf-8 -*-

import re
import inspect
from neomodel.match import Traversal
from neomodel.match import OUTGOING, INCOMING, EITHER


def build_relation_string(lhs, rhs, ident=None, relation_type=None, direction=None, props=None, **kwargs):
    """
    Generate a relationship matching string, with specified parameters.
    
    Basically a rewrite of ``neomodel.match._rel_helper`` except that it 
    returns a string suitable for doing string formatting on.
    
    :param lhs: The left hand statement.
    :type lhs: str
    :param rhs: The right hand statement.
    :type rhs: str
    :param ident: A specific identity to name the relationship, or None.
    :type ident: str
    :param relation_type: None for all direct rels, * for all of any length, or a name of an explicit rel.
    :type relation_type: str
    :param direction: None or EITHER for all OUTGOING,INCOMING,EITHER. Otherwise OUTGOING or INCOMING.
    :param props: dictionary of relationship properties to match
    :returns: The calculated relationship string
    :rtype str
    """
    direction_map = {
        OUTGOING: '-{0}->',
        INCOMING: '<-{0}-',
        EITHER: '-{0}-'
    }

    props = props or {}
    relation_props = ' {{{{{0}}}}}'.format(', '.join(
        ['{}: {}'.format(key, value) for key, value in props.items()]))

    statement = direction_map[direction or 0]
    if relation_type is None:
        statement = statement.format('')
    elif relation_type == '*':
        statement = statement.format('[*]')
    else:
        statement = statement.format('[%s:%s%s]' % (ident if ident else '', relation_type, relation_props))
    return '({0}){1}({2})'.format(lhs, statement, rhs)


class PathManager:
    """
    Class for building traversal paths for node instances
    managed by chemtrails.
    """
    def __init__(self, source):
        # Keep a list of all calculated matching strings.
        self._statements = []

        # Keep track of the next source class.
        self._next_class = source

    @property
    def traversals(self):
        """
        Returns a list of valid ``Traversal`` instances
        for the current nodeset.
        """
        source_class = self.next_class
        return list(filter(lambda prop: isinstance(prop, Traversal),
                           source_class.nodes.__dict__.values()))

    @property
    def next_class(self):
        return self._next_class

    @next_class.setter
    def next_class(self, klass):
        self._next_class = klass

    @property
    def statement(self):
        """
        :returns: The final calculated relationship statement or None if no
                  relation types has been added.
        :rtype: None or str
        """
        if not self._statements:
            return None

        def format_node(ident, label, **filters):
            if not filters:
                return '{0}: {1}'.format(ident, label)
            else:
                label = '{0} {{{1}}}'.format(
                    label, ', '.join(['{}: {}'.format(
                        key, '"%s"' % value if isinstance(value, str) else value)
                        for key, value in filters.items()])
                )
                return '{0}: {1}'.format(ident, label)

        # Matches ie. (source1: UserNode) as long as it's followed
        # by a "-[" which indicates the beginning of a relationship.
        regex = r'^(\(source\d+:.\w+\)(?=-\[))'

        statements = []
        for n, config in enumerate(self._statements):
            # Replace placeholders with actual values.
            defaults = config['params'].copy()

            source_props = config['source_props']
            if not inspect.isclass(config['source_class']):
                # If we have a node instance, always match its primary key!
                source_props['pk'] = config['source_class'].pk

            target_props = config['target_props']

            defaults.update({
                'source': 'source{0}'.format(format_node(
                    ident=n,
                    label=config['source_class'].__label__,
                    **source_props
                )),
                'target': 'target{0}'.format(format_node(
                    ident=n,
                    label=config['target_class'].__label__,
                    # Add any user specified filters to target node.
                    **target_props
                ))
            })
            relation_str = config['atom'].format(**defaults)
            if n == 0:
                statements.append(relation_str)
                continue

            # Remove the source node definition from string.
            # It's already specified in the previous element.
            statements.append(re.sub(regex, '', relation_str))

        return ''.join(statements)

    def add(self, relation_type=None, properties=None, source_props=None, **filters):
        """
        Adds a relationship matching string, based on relation type.
        
        :param relation_type: The relationship type, ie USER.
        :type relation_type: str
        :param properties: Optional properties used to instantiate the
          ``StructuredRel`` relationship class. This is used to gather properties 
          for the generated relationship statement.
        :type properties: dict
        :param source_props: Property mapping which should be applied for filtering the
          source node.
        :type source_props: dict
        :param filters: Filters which should be applied to the relations types end node.
        :type filters: dict
        :returns: self
        """
        traversal = self.get_traversal(relation_type)
        if traversal is None:
            if not relation_type:
                raise Exception('Cannot find relationship with empty relation type.')
            raise Exception('%(klass)r has no relation type %(relation_type)s' % {
                'klass': self.next_class,
                'relation_type': relation_type
            })

        model = traversal.definition['model']
        properties = properties or {}

        # Instantiate a fake relationship model in order
        # to pick attributes for the relationship.
        fake = model(**properties)
        params = {prop: '"%s"' % value if isinstance(value, str) else value
                  for prop, value in model.deflate(fake.__properties__).items()}
        relation_properties = {key: '{{{0}}}'.format(key) for key in params.keys()}

        self._statements.append({
            'source_class': self.next_class,
            'source_props': source_props or {},
            'target_class': traversal.target_class,
            'target_props': filters,
            'params': params,
            'atom': build_relation_string(lhs='{source}', rhs='{target}',
                                          props=relation_properties, **traversal.definition)
        })
        self.next_class = traversal.target_class
        return self

    def get_traversal(self, relation_type):
        """
        Returns the first traversal instance matching ``relation_type``.
        """
        for traversal in self.traversals:
            if traversal.definition['relation_type'] == relation_type:
                return traversal
        return None
    
    def get_path(self):
        """
        :returns: The calculated statement as MATCH path = (...) RETURN path
        :rtype str
        """
        if not self.statement:
            raise AttributeError('No calculated statements.')
        return 'MATCH path = {statement} RETURN path;'.format(statement=self.statement)

    def get_match(self):
        if not self.statement:
            raise AttributeError('No calculated statements.')
        return 'MATCH {statement} RETURN *;'.format(statement=self.statement)
