# -*- coding: utf-8 -*-

import re
import inspect

from django.contrib.contenttypes.fields import GenericForeignKey
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
        self.source = source

        # Keep a list of all calculated matching strings.
        self._statements = []

        # Keep track of the next source class.
        self.___next_class__ = source

        # Override default direction. If set to -1, 0 or 1 this
        # will affect **all** directions in the query!
        self.__direction__ = None

    @property
    def traversals(self):
        """
        Returns a list of valid ``Traversal`` instances
        for the current nodeset.
        """
        return list(filter(lambda prop: isinstance(prop, Traversal),
                           self.next_class.nodes.__dict__.values()))

    @property
    def next_class(self):
        return self.___next_class__

    @next_class.setter
    def next_class(self, klass):
        self.___next_class__ = klass

    @property
    def direction(self):
        return self.__direction__

    @direction.setter
    def direction(self, direction):
        self.__direction__ = direction

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
            separator = ': ' if label else ''
            if not label and not filters:
                return '{0}'.format(ident)
            elif not filters:
                return '{0}: {1}'.format(ident, label)
            else:
                label = '{0} {{{1}}}'.format(
                    label if label else '', ', '.join(['{}: {}'.format(
                        key, '"%s"' % value if isinstance(value, str) else value)
                        for key, value in filters.items()])
                )
                return '{0}{1}{2}'.format(ident, separator, label)

        # Matches ie. (source1: UserNode {...}) as long as it's followed
        # by a "-[" or "<-[" which indicates the beginning of a relationship.
        pattern = re.compile(r'^(\(source\d+:.\w+(.{\w+:.[A-Za-z0-9\'"_]+})?\)(?=<?-\[))')

        statements = []
        for n, config in enumerate(self._statements):
            # Replace placeholders with actual values.
            defaults = config['relation_props'].copy()

            # Check if we should override direction
            if self.direction is not None:
                assert self.direction in (INCOMING, EITHER, OUTGOING), (
                    'Direction must be one of %s.' % ', '.join((INCOMING, EITHER, OUTGOING)))
                config['traversal'].definition['direction'] = self.direction

            atom = build_relation_string(lhs='{source}', rhs='{target}',
                                         props={key: '{{{0}}}'.format(key) for key in defaults.keys()},
                                         **config['traversal'].definition)

            source_props = self.resolve_filters(config['source_props'])
            if not inspect.isclass(config['source_class']):
                # If we have a node instance, always match its primary key!
                if getattr(config['source_class'], 'pk', None):
                    source_props['pk'] = config['source_class'].pk

            target_props = self.resolve_filters(config['target_props'])

            defaults.update({
                'source': 'source{0}'.format(format_node(
                    ident=n,
                    label=(config['source_class'].__label__
                           if config['source_class'] else None),
                    **source_props
                )),
                'target': 'target{0}'.format(format_node(
                    ident=config.get('target_index', n),
                    label=(config['target_class'].__label__
                           if config['target_class'] else None),
                    # Add any user specified filters to target node.
                    **target_props
                ))
            })

            relation_str = atom.format(**defaults)
            if n == 0:
                statements.append(relation_str)
                continue

            # Remove the source node definition from string.
            # It's already specified in the previous element.
            statements.append(pattern.sub('', relation_str))

        return ''.join(statements)

    def add(self, relation_type=None, relation_props=None, source_props=None, target_props=None):
        """
        Adds a relationship matching string, based on relation type.
        
        :param relation_type: The relationship type, ie USER.
        :type relation_type: str
        :param relation_props: Optional properties used to instantiate the
          ``StructuredRel`` relationship class. This is used to gather properties 
          for the generated relationship statement.
        :type relation_props: dict
        :param source_props: Property mapping which should be applied for filtering the
          source node.
        :type source_props: dict
        :param target_props: Property mapping which should be applied for filtering the
          target node.
        :type target_props: dict
        :returns: self
        """
        defaults = {}
        traversal = self.get_traversal(relation_type)
        if traversal is None:
            # Check if using any back-references like ie. {0:GROUPS}
            pattern = re.compile(r'(?<=^{)(\d:\w+)(?=})')
            match = pattern.search(relation_type)
            if match:
                index, relation_type = match.group().split(':')
                index = int(index)
                traversal = self.get_traversal(relation_type)
                if len(self._statements) - 1 < index:
                    raise IndexError('target index out of range')
                defaults['target_index'] = index
            elif not relation_type:
                raise ValueError('Cannot find relationship with empty relation type.')
            if traversal is None:
                raise AttributeError('%(klass)r has no relation type %(relation_type)s' % {
                    'klass': self.next_class,
                    'relation_type': relation_type
                })

        model = traversal.definition['model']
        relation_props = relation_props or {}

        # Instantiate a fake relationship model in order
        # to pick attributes for the relationship.
        fake = model(**relation_props)
        relation_props = {prop: '"%s"' % value if isinstance(value, str) else value
                          for prop, value in model.deflate(fake.__properties__).items()}

        # At this point we have no idea of what object the GenericForeignKey
        # relationship is really pointing at.
        remote_field = getattr(traversal.source_class.Meta.model,
                               model.remote_field.default.split('.')[-1])
        if isinstance(remote_field, GenericForeignKey):
            del relation_props['target_field']

        defaults.update({
            'source_class': self.next_class,
            'source_props': source_props or {},
            'target_class': (traversal.target_class
                             if not isinstance(remote_field, GenericForeignKey) else None),
            'target_props': target_props or {},
            'relation_props': relation_props,
            'traversal': traversal,
        })
        self._statements.append(defaults)
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

    def resolve_filters(self, filters):
        """
        Check if the filter contains any special variables and resolve them.
        Currently only supports resolving parameters using "{source}" variable,
        which will inspect the originating node.

        Ex:
          filters = {'username': '{source}.username'}

          This will replace the '{source}.pk' value with whatever value is found
          on the 'username' attribute on the source node.

        :param filters: Mapping with filter to inspect
        :type filters: dict
        :returns: Dictionary with resolved values.
        """
        pattern = re.compile(r'(?<={source}.)\w+')  # Matches '{source}.attribute'
        for attr, value in filters.items():
            try:
                match = pattern.search(value)
                if match:
                    key = match.group()
                    if key not in self.source.defined_properties(aliases=False, rels=False):
                        raise AttributeError("%(node)r has no valid property named '%(key)s'. "
                                             "Make sure the '%(value)s' targets a valid attribute." % {
                                                 'node': self.source, 'key': key, 'value': value
                                             })
                    value = getattr(self.source, key)
                    if value is None:
                        value = 'null'
                    filters[attr] = value
            except TypeError:
                # This can happen if trying to re-process an already processed filter.
                continue

        return filters
