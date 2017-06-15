# -*- coding: utf-8 -*-

import itertools
import logging
import operator
from collections import defaultdict
from functools import reduce

from django.db import models
from django.db.models import Manager
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured, ValidationError, ObjectDoesNotExist
from django.contrib.postgres.fields import ArrayField, HStoreField, JSONField, RangeField
from django.utils.translation import ungettext

from neomodel import *
from chemtrails import settings
from chemtrails.utils import get_model_string, flatten, timeit

logger = logging.getLogger(__name__)

field_property_map = {
    models.ForeignKey: RelationshipTo,
    models.OneToOneField: RelationshipTo,
    models.ManyToManyField: RelationshipTo,
    models.ManyToOneRel: RelationshipTo,
    models.OneToOneRel: RelationshipTo,
    models.ManyToManyRel: RelationshipTo,
    # GenericForeignKey: RelationshipTo,  # TODO: Implement
    GenericRelation: RelationshipTo,

    models.AutoField: IntegerProperty,
    models.BigIntegerField: IntegerProperty,
    models.BooleanField: BooleanProperty,
    models.CharField: StringProperty,
    models.CommaSeparatedIntegerField: ArrayProperty,
    models.DateField: DateProperty,
    models.DateTimeField: DateTimeProperty,
    models.DecimalField: FloatProperty,
    models.DurationField: StringProperty,
    models.EmailField: StringProperty,
    models.FilePathField: StringProperty,
    models.FileField: StringProperty,
    models.FloatField: FloatProperty,
    models.GenericIPAddressField: StringProperty,
    models.IntegerField: IntegerProperty,
    models.IPAddressField: StringProperty,
    models.NullBooleanField: BooleanProperty,
    models.PositiveIntegerField: IntegerProperty,
    models.PositiveSmallIntegerField: IntegerProperty,
    models.SlugField: StringProperty,
    models.SmallIntegerField: IntegerProperty,
    models.TextField: StringProperty,
    models.TimeField: IntegerProperty,
    models.URLField: StringProperty,
    models.UUIDField: StringProperty,

    # PostgreSQL special fields
    # ArrayField: ArrayProperty,
    HStoreField: JSONProperty,
    JSONField: JSONProperty
}


class Meta(type):
    """
    Meta class template.
    """
    model = None
    app_label = None

    def __new__(mcs, name, bases, attrs):
        cls = super(Meta, mcs).__new__(mcs, str(name), bases, attrs)
        return cls


class NodeBase(NodeMeta):
    """
    Base Meta class for ``StructuredNode`` which adds a model class.
    """
    creation_counter = 0

    def __new__(mcs, name, bases, attrs):
        cls = super(NodeBase, mcs).__new__(mcs, str(name), bases, attrs)
        cls.creation_counter = NodeBase.creation_counter
        NodeBase.creation_counter += 1

        if getattr(cls, 'Meta', None):
            meta = Meta('Meta', (Meta,), dict(cls.Meta.__dict__))

            # A little hack which helps us dynamically create ModelNode classes
            # where variables holding the model class is out of scope.
            if hasattr(cls, '__metaclass_model__') and not meta.model:
                meta.model = getattr(cls, '__metaclass_model__', None)
                delattr(cls, '__metaclass_model__')

            if not getattr(meta, 'model', None):
                raise ValueError('%s.Meta.model attribute cannot be None.' % name)

            if getattr(meta, 'app_label', None) is None:
                meta.app_label = meta.model._meta.app_label

            cls.add_to_class('Meta', meta)

        elif not getattr(cls, '__abstract_node__', None):
            raise ImproperlyConfigured('%s must implement a Meta class.' % name)

        return cls

    def add_to_class(cls, name, value):
        setattr(cls, name, value)

    @staticmethod
    def get_model_permissions(model):
        default_permissions = ['{perm}_{object_name}'.format(perm=p, object_name=model._meta.object_name.lower())
                               for p in model._meta.default_permissions]
        return sorted(set(itertools.chain(map(operator.itemgetter(0), model._meta.permissions), default_permissions)))


class ModelNodeMeta(NodeBase):
    """
    Meta class for ``ModelNode``.
    """

    def __new__(mcs, name, bases, attrs):
        cls = super(ModelNodeMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set class name and label for node
        cls.__name__ = cls.__label__ = '{object_name}Node'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.type = StringProperty(default='ModelNode')
        cls.pk = cls.get_property_class_for_field(cls._pk_field.__class__)(unique_index=True)
        cls.app_label = StringProperty(default=cls.Meta.app_label)
        cls.model_name = StringProperty(default=cls.Meta.model._meta.model_name)

        forward_relations = cls.get_forward_relation_fields()
        reverse_relations = cls.get_reverse_relation_fields()

        # Add to cache before recursively looking up relationships.
        from chemtrails.neoutils import __node_cache__
        if cls.Meta.model not in __node_cache__:
            __node_cache__.update({cls.Meta.model: cls})

        for field in cls.Meta.model._meta.get_fields():

            if field.__class__ not in field_property_map:
                continue

            # Add forward relations
            if field in forward_relations:
                relation = cls.get_related_node_property_for_field(field)
                if relation:
                    cls.add_to_class(field.name, relation)

            # Add reverse relations
            elif field in reverse_relations:
                relation = cls.get_related_node_property_for_field(field)
                if relation:
                    cls.add_to_class(field.related_name or '%s_set' % field.name, relation)

            # Add concrete fields
            else:
                if field is not cls._pk_field:
                    cls.add_to_class(field.name, cls.get_property_class_for_field(field.__class__)())

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        install_labels(cls, quiet=True, stdout=None)
        return cls


class ModelNodeMixinBase:
    """
    Base mixin class
    """
    def __update_raw_node__(self):
        """
        Compares the node class attributes to raw node attributes and removes
        any artifacts from the raw node. We want the defined node class 
        attributes to be the source of truth at all times.
        :returns None
        """
        # We can only operate on bound nodes
        if not self._is_bound:
            return

        query = ' '.join((
            'MATCH (n:{label}) WHERE ID(n) = {id}'.format(label=self.__label__, id=self.id),
            'OPTIONAL MATCH (n)-[r]->() RETURN n, r'
        ))
        results, _ = db.cypher_query(query)

        # Identify all properties and relationships which exists on the raw node,
        # but which are not defined on the class model.
        to_remove = defaultdict(set)
        for node, relation in results:

            if not node or node.id in to_remove:
                continue

            for prop in node.properties.keys():
                if prop not in self.defined_properties(aliases=False, rels=False):
                    to_remove[node.id].add(prop)

            relationships = [r.definition['relation_type'] for r in
                             self.defined_properties(aliases=False, properties=False).values()]
            if relation is not None and relation.type not in relationships:
                query = 'MATCH (n:{label})-[r]-() WHERE ID(n) = {id} AND ID(r) = {rid} DELETE r'.format(**{
                    'label': self.__label__,
                    'id': node.id,
                    'rid': relation.id
                })
                db.cypher_query(query)
                logger.info('Relationship type %(type)s is not defined on %(klass)s. '
                            'Removed relationship from raw node.' % {
                                'type': relation.type,
                                'klass': self.__class__.__name__
                            })

            if node.id in to_remove:
                query = ' '.join((
                    'MATCH (n:{label}) WHERE ID(n) = {id} REMOVE'.format(label=self.__label__, id=node.id),
                    ', '.join(['n.%s' % prop for prop in to_remove[node.id]])
                ))
                db.cypher_query(query)
                logger.info('The following %(text)s %(props)s is not defined on %(klass)s. '
                            'Removed %(props)s from raw node.' % {
                                'text': ungettext('property', 'properties', len(to_remove[node.id])),
                                'props': ', '.join([prop for prop in to_remove[node.id]]),
                                'klass': self.__class__.__name__
                            })

    @classproperty
    def _pk_field(cls):
        model = cls.Meta.model
        pk_field = reduce(operator.eq,
                          filter(lambda field: field.primary_key, model._meta.fields))
        return pk_field

    @classproperty
    def _is_ignored(cls):
        lookups = (
            cls.Meta.app_label,
            '{app_label}.*'.format(app_label=cls.Meta.app_label),
            get_model_string(cls.Meta.model)
        )
        return any(match in settings.IGNORE_MODELS for match in lookups)

    @classproperty
    def has_relations(cls):
        return len(cls.__all_relationships__) > 0

    @property
    def paths(self):
        """
        Returns a ``PathManager`` object which can be used to build 
        traversal paths originating from this node.
        """
        from chemtrails.neoutils.managers import PathManager
        return PathManager(self)

    @staticmethod
    def _log_relationship_definition(action: str, node, prop, level: int = 20):
        direction = {-1: 'INCOMING', 0: 'MUTUAL', 1: 'OUTGOING'}
        message = ('%(action)s %(direction)s relation %(relation_type)s '
                   'between %(klass)r and %(node)r' % {
                       'action': action,
                       'direction': direction[prop.definition['direction']],
                       'relation_type': prop.definition['relation_type'],
                       'klass': prop.source,
                       'node': node
                   })
        logger.log(level=level, msg=message)

    @staticmethod
    def _get_remote_field_name(field):
        reverse_field = True if isinstance(field, (
            models.ManyToManyRel, models.ManyToOneRel, models.OneToOneRel, GenericRelation)) else False

        return str('{model}.{field}'.format(
            model=get_model_string(field.model),
            field=(field.related_name or '%s_set' % field.name
                   if not isinstance(field, (models.OneToOneRel, GenericRelation)) else field.name))
                   if reverse_field else field.remote_field.field).lower()

    @staticmethod
    def get_property_class_for_field(klass):
        """
        Returns the appropriate property class for field class.
        :param klass: Field class which to look up Property type for.
        """
        if klass in field_property_map:
            return field_property_map[klass]
        else:
            # If ``klass`` not found in the field mapping, inspect it's bases
            # and return the first matching base class.
            # NOTE: This might not be very safe, so perhaps we should find a better way.
            for base in klass.__bases__:
                if base in field_property_map:
                    return field_property_map[base]

            # If we're reaching this point we've got a field with an unknown
            # base class. Final attempt at identifying the class type.
            if issubclass(klass, RangeField) and hasattr(klass, 'base_field'):
                # Looks like a PostgreSQL RangeField
                if klass.base_field in field_property_map:
                    return field_property_map[klass.base_field]

        raise NotImplementedError('Unsupported field. Field %s is currently not supported.' % klass.__name__)

    @classmethod
    def get_forward_relation_fields(cls):
        return [
            field for field in cls.Meta.model._meta.get_fields()
            if field.is_relation and (
                not field.auto_created or field.concrete
                or field.one_to_one
                or (field.many_to_one and field.related_model)
            )
        ]

    @classmethod
    def get_reverse_relation_fields(cls):
        return [
            field for field in cls.Meta.model._meta.get_fields()
            if field.auto_created and not field.concrete and (
                field.one_to_many
                or field.many_to_many
                or field.one_to_one
            )
        ]

    @classmethod
    def get_relationship_type(cls, field):
        """
        Get the relationship type for field. If ``settings.NAMED_RELATIONSHIPS``
        is True, pick the relationship type from the field. If not,
        use a pre-defined set of generic types.
        """
        generic_types = {
            Relationship: 'MUTUAL_RELATION',
            RelationshipTo: 'RELATES_TO',
            RelationshipFrom: 'RELATES_FROM'
        }
        if settings.NAMED_RELATIONSHIPS:
            return '{related_name}'.format(
                related_name=getattr(field, 'related_name', field.name) or field.name).upper()
        else:
            prop = cls.get_property_class_for_field(field.__class__)
            return generic_types[prop]

    @classmethod
    def get_related_node_property_for_field(cls, field, meta_node=False):
        """
        Get the relationship definition for the related node based on field.
        :param field: Field to inspect
        :param meta_node: If True, return the meta node for the related model,
                          else return the model node.
        :returns: A ``RelationshipDefinition`` instance.
        """
        from chemtrails.neoutils import (
            __meta_cache__, __node_cache__,
            get_node_class_for_model, get_meta_node_class_for_model
        )

        reverse_field = True if isinstance(field, (
            models.ManyToManyRel, models.ManyToOneRel, models.OneToOneRel, GenericRelation)) else False

        class DynamicRelation(StructuredRel):
            type = StringProperty(default=field.__class__.__name__)
            is_meta = BooleanProperty(default=meta_node)
            remote_field = StringProperty(default=cls._get_remote_field_name(field))
            target_field = StringProperty(default=str(getattr(field, 'target_field', '')).lower())  # NOTE: Workaround for #27

        prop = cls.get_property_class_for_field(field.__class__)
        relationship_type = cls.get_relationship_type(field)

        if meta_node:
            klass = (__meta_cache__[field.related_model]
                     if field.related_model in __meta_cache__
                     else get_meta_node_class_for_model(field.related_model))
            return (prop(cls_name=klass, rel_type=relationship_type, model=DynamicRelation)
                    if not klass._is_ignored else None)
        else:
            klass = (__node_cache__[field.related_model]
                     if reverse_field and field.related_model in __node_cache__
                     else get_node_class_for_model(field.related_model))
            return (prop(cls_name=klass, rel_type=relationship_type, model=DynamicRelation)
                    if not klass._is_ignored else None)

    def sync(self, *args, **kwargs):
        """
        Responsible for syncing the node class with Neo4j.
        """
        raise NotImplementedError('This method must be implemented in derived class!')


class ModelNodeMixin(ModelNodeMixinBase):

    def __init__(self, instance=None, bind=True, *args, **kwargs):
        self._instance = instance
        self.__recursion_depth__ = 0

        defaults = {key: getattr(self._instance, key, kwargs.get(key, None))
                    for key, _ in self.__all_properties__}
        kwargs.update(defaults)
        super(ModelNodeMixinBase, self).__init__(self, *args, **kwargs)

        # Never try to bind ignore nodes
        if bind and self._is_ignored:
            bind = False

        # Query the database for an existing node and set the id if found.
        # This will make this a "bound" node.
        if bind and not hasattr(self, 'id') and getattr(self, 'pk', None) is not None:
            node_id = self._get_id_from_database(self.deflate(self.__properties__))
            if node_id:
                self.id = node_id
            if not self._instance:
                # If instantiated without an instance, try to look it up.
                self._instance = self.get_object(self.pk)

    def __repr__(self):
        return '<{label}: {id}>'.format(label=self.__class__.__label__, id=self.id if self._is_bound else None)

    def to_csv(self, cntr=0, target_file=None):
        from chemtrails.neoutils import get_node_for_object
        import csv

        def format_prop(prop_list):
            formated_string = ''
            first = True
            for name, value in prop_list.items():
                if hasattr(value, 'default') and isinstance(value, Property):

                    attr = getattr(self, name, None)

                    if attr is None and value.has_default is False:
                        continue

                    if first:
                        first = False
                    else:
                        formated_string += ', '

                    formated_string += name + ': '

                    v = value.deflate(value=attr)

                    if value.default is None:
                        if isinstance(v, str):
                            formated_string += '\'{value}\''.format(
                                value=v.replace('"', r'\"').replace("'", r"\'"))
                        else:
                            formated_string += str(v)
                    elif isinstance(value, StringProperty):
                        formated_string += '\'{value}\''.format(
                            value=value.default.replace('"', r'\"').replace("'", r"\'"))
                    else:
                        formated_string += str(value.default)

            return formated_string

        prop = self.defined_properties(aliases=False, rels=False)

        source_node_name = self.__label__
        source_node_pk = self.pk

        with open(target_file.name, 'a', newline='') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=';',
                                    quotechar='|', quoting=csv.QUOTE_MINIMAL)

            queryparams = format_prop(prop)
            spamwriter.writerow(['n'] + ['CREATE (:%s { %s })' % (self.__label__, queryparams)])

            rels = self.defined_properties(aliases=False, properties=False)

            for name, obj in rels.items():

                relation_type = obj.definition['relation_type']
                obj_attr = getattr(self._instance, name)

                if isinstance(obj_attr, models.Model):

                    node = get_node_for_object(obj_attr, False)
                    target_node_name = node.__label__
                    target_node_pk = node.pk
                    label_a = source_node_name + str(cntr) + str(source_node_pk)
                    label_b = target_node_name + str(cntr) + str(target_node_pk)
                    label_a = label_a.replace('-', '_')
                    label_b = label_b.replace('-', '_')

                    rel_props = format_prop(obj.definition['model'].__dict__)

                    spamwriter.writerow(
                        ['r'] + [('MATCH({node_a} {{ pk: {node_a_pk} }}), ({node_b} {{ pk: {node_b_pk} }}) '
                                  'WITH {node_a_label}, {node_b_label} '
                                  'CREATE UNIQUE({node_a_label})-[r:{rel}{{{rel_prop}}}]->({node_b_label})'
                                  .format(**{'node_a': label_a + ':' + source_node_name,
                                             'node_a_pk': '"{pk}"'.format(pk=source_node_pk) if isinstance(source_node_pk, str) else source_node_pk,
                                             'node_a_label': label_a,
                                             'node_b': label_b + ':' + target_node_name,
                                             'node_b_pk': '"{pk}"'.format(pk=target_node_pk) if isinstance(target_node_pk, str) else target_node_pk,
                                             'node_b_label': label_b,
                                             'rel': relation_type,
                                             'rel_prop': rel_props
                                             })
                                  )
                                 ]
                    )
                    cntr = cntr + 1

                elif isinstance(obj_attr, Manager):
                    for item in obj_attr.all():
                        i = item

                        node = get_node_for_object(i, False)
                        target_node_name = node.__label__
                        target_node_pk = node.pk
                        label_a = 'a' + str(cntr)
                        label_b = 'b' + str(cntr)
                        label_a = label_a.replace('-', '_')
                        label_b = label_b.replace('-', '_')
                        rel_props = format_prop(obj.definition['model'].__dict__)

                        spamwriter.writerow(
                            ['r'] + [('MATCH({node_a} {{ pk: {node_a_pk} }}), ({node_b} {{ pk: {node_b_pk} }}) '
                                      'WITH {node_a_label}, {node_b_label} '
                                      'CREATE UNIQUE({node_a_label})-[r:{rel}{{{rel_prop}}}]->({node_b_label})'
                                      .format(**{'node_a': label_a + ':' + source_node_name,
                                                 'node_a_pk': '"{pk}"'.format(pk=source_node_pk) if isinstance(source_node_pk, str) else source_node_pk,
                                                 'node_a_label': label_a,
                                                 'node_b': label_b + ':' + target_node_name,
                                                 'node_b_pk': '"{pk}"'.format(pk=target_node_pk) if isinstance(target_node_pk, str) else target_node_pk,
                                                 'node_b_label': label_b,
                                                 'rel': relation_type,
                                                 'rel_prop': rel_props
                                                 })
                                      )
                                     ]
                        )
                        cntr = cntr + 1

    @property
    def _is_bound(self):
        return getattr(self, 'id', None) is not None

    @property
    def _recursion_depth(self):
        return self.__recursion_depth__

    @_recursion_depth.setter
    def _recursion_depth(self, n):
        self.__recursion_depth__ = n

    def _get_id_from_database(self, params):
        """
        Query for node and return id.
        :param params: Parameters to use in query.
        :returns: Node id if found, else None
        """
        query = ' '.join(('MATCH (n:{label}) WHERE'.format(label=self.__label__),
                          ' AND '.join(['n.{} = {{{}}}'.format(key, key) for key in params.keys()]),
                          'RETURN id(n) LIMIT 1'))
        result, _ = db.cypher_query(query, params)
        return list(flatten(result))[0] if result else None

    def get_object(self, pk=None):
        """
        :returns: Django model instance if found or None
        """
        try:
            return self._instance or ContentType.objects.get(
                app_label=self.app_label, model=self.model_name).get_object_for_this_type(
                pk=pk or getattr(self, 'pk', None))
        except ObjectDoesNotExist:
            return None

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []

        props = self.__properties__
        for key in exclude:
            if key in props:
                del props[key]

        try:
            self.deflate(props, self)

            if validate_unique:
                cls = self.__class__
                unique_props = [attr for attr, prop in self.defined_properties(aliases=False, rels=False).items()
                                if prop not in exclude and prop.unique_index]
                for key in unique_props:
                    value = self.deflate({key: props[key]}, self)[key]
                    node = cls.nodes.get_or_none(**{key: value})

                    # If exists and not this node
                    if node and node.id != getattr(self, 'id', None):
                        raise ValidationError({key, 'already exists'})

        except DeflateError as e:
            raise ValidationError({e.property_name: e.msg})
        except RequiredProperty as e:
            raise ValidationError({e.property_name: 'is required'})

    @timeit
    def recursive_connect(self, max_depth=settings.MAX_CONNECTION_DEPTH):
        """
        Recursively connect a node branch.
        :param max_depth: Go n nodes deep originating from the current node.
        :returns: None
        """
        from chemtrails.neoutils import get_node_for_object

        def connect(node, prop):
            """
            Connect both sides of the relationship.
            """
            if node not in prop.all() and isinstance(node, prop.definition['node_class']):
                prop.connect(node)
                self._log_relationship_definition('Connected', node, prop)
                for p, r in node.defined_properties(aliases=False, properties=False).items():
                    p = getattr(node, p)
                    if issubclass(p.definition['node_class'], self.__class__):
                        # Make sure we only connects the "reverse" relation of ``prop``.
                        remote_field = p.definition['model'].remote_field
                        target_field = p.definition['model'].target_field

                        reverse_fields = p.source_class.get_reverse_relation_fields()
                        forward_fields = p.source_class.get_forward_relation_fields()

                        for f in itertools.chain(reverse_fields, forward_fields):
                            if f.__class__ not in field_property_map:
                                continue
                            if (remote_field.default == p.source_class._get_remote_field_name(f)
                                    and target_field.default == str(getattr(f, 'target_field', '')).lower()):
                                p.connect(self)
                                self._log_relationship_definition('Connected', self, p)

        def disconnect(node, prop):
            """
            Disconnect both sides of the relationship.
            """
            prop.disconnect(node)
            self._log_relationship_definition('Disconnected', node, prop)
            for p, r in node.defined_properties(aliases=False, properties=False).items():
                p = getattr(node, p)
                if issubclass(p.definition['node_class'], self.__class__):
                    # Make sure we only disconnects the "reverse" relation of ``prop``.
                    remote_field = p.definition['model'].remote_field
                    target_field = p.definition['model'].target_field

                    reverse_fields = p.source_class.get_reverse_relation_fields()
                    forward_fields = p.source_class.get_forward_relation_fields()

                    for f in itertools.chain(reverse_fields, forward_fields):
                        if f.__class__ not in field_property_map:
                            continue
                        if (remote_field.default == p.source_class._get_remote_field_name(f)
                                and target_field.default == str(getattr(f, 'target_field', '')).lower()):
                            p.disconnect(self)
                            self._log_relationship_definition('Disconnected', self, p)

        if max_depth <= 0:
            logger.debug('Reached MAX DEPTH for %(node)r, returning...' % {'node': self})
            return

        # We require a model instance to look for filter values.
        instance = self.get_object(self.pk)
        if not instance:
            return

        for attr, relation in self.defined_properties(aliases=False, properties=False).items():
            prop = getattr(self, attr)
            klass = relation.definition['node_class']

            source = getattr(instance, prop.name, None)
            if not source:
                for node in prop.all():
                    disconnect(node, prop)
                continue

            if isinstance(source, models.Model):
                node = klass.nodes.get_or_none(pk=source.pk)
                if not node:
                    node = get_node_for_object(source).save()
                    logger.info('Created missing node %(node)r while synchronizing %(instance)r' % {
                        'node': node,
                        'instance': instance
                    })
                connect(node, prop)
                node.recursive_connect(max_depth=max_depth - 1)

            elif isinstance(source, Manager):
                if not source.exists():
                    to_disconnect = prop.filter(
                        pk__in=list(source.model._meta.default_manager.exclude(pk__in=source.values('pk'))
                                    .values_list('pk', flat=True)))
                    for n in to_disconnect:
                        disconnect(n, prop)
                    continue

                nodeset = klass.nodes.filter(pk__in=list(source.values_list('pk', flat=True)))
                if len(nodeset) != source.count():
                    existing = [n.pk for n in nodeset]
                    for obj in source.exclude(pk__in=existing):
                        node = get_node_for_object(obj).save()
                        logger.info('Created missing node %(node)r while synchronizing %(instance)r' % {
                            'node': node,
                            'instance': instance
                        })
                    nodeset = klass.nodes.filter(pk__in=list(source.values_list('pk', flat=True)))

                for node in nodeset:
                    connect(node, prop)
                    node.recursive_connect(max_depth=max_depth - 1)

    def sync(self, max_depth=settings.MAX_CONNECTION_DEPTH, update_existing=True, create_empty=False):
        """
        Synchronizes the current node with data from the database and
        connect all directly related nodes.
        :param max_depth: Maximum depth of recursive connections to be made.
        :param update_existing: If True, save data from the django model to graph node.
        :param create_empty: If the Node has no relational fields, don't create it.
        :returns: The ``ModelNode`` instance or None if not created.
        """
        cls = self.__class__

        if self._is_ignored:
            try:
                self.delete()
            except ValueError:
                pass
            finally:
                return None

        if not cls.has_relations and not create_empty:
            return None

        self.full_clean(validate_unique=not update_existing)

        if update_existing:
            if not self._is_bound:
                node = cls.nodes.get_or_none(**{'pk': self.pk})
                if node:
                    self.id = node.id
            if self._instance is not None:
                # Update the node instance with data from object instance
                # whenever we're syncing.
                defaults = {key: getattr(self._instance, key, None)
                            for key, _ in self.__all_properties__ if hasattr(self._instance, key)}
                for key, value in defaults.items():
                    setattr(self, key, value)

            # Make sure the neo4j node properties and relationships matches
            # the class definition.
            self.__update_raw_node__()

            # Finally save the node.
            self.save()

        # Connect relations
        self.recursive_connect(max_depth=max_depth)

        return self


class MetaNodeMeta(NodeBase):
    """
    Meta class for ``MetaNode``.
    """

    def __new__(mcs, name, bases, attrs):
        cls = super(MetaNodeMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set class name and label for node
        cls.__name__ = cls.__label__ = '{object_name}'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.type = StringProperty(default='MetaNode')
        cls.label = StringProperty(default=cls.Meta.model._meta.label, unique_index=True)
        cls.app_label = StringProperty(default=cls.Meta.model._meta.app_label)
        cls.model_name = StringProperty(default=cls.Meta.model._meta.model_name)
        cls.model_permissions = ArrayProperty(default=cls.get_model_permissions(cls.Meta.model))
        cls.is_intermediary = BooleanProperty(default=not ContentType.objects.filter(
            app_label=cls.Meta.model._meta.app_label, model=cls.Meta.model._meta.model_name).exists())

        forward_relations = cls.get_forward_relation_fields()
        reverse_relations = cls.get_reverse_relation_fields()

        # Add to cache before recursively looking up relationships.
        from chemtrails.neoutils import __meta_cache__
        if cls.Meta.model not in __meta_cache__:
            __meta_cache__.update({cls.Meta.model: cls})

        # # Add relations for the model
        for field in itertools.chain(forward_relations, reverse_relations):

            if field.__class__ not in field_property_map:
                continue

            # Add forward relations
            if field in forward_relations:
                relation = cls.get_related_node_property_for_field(field, meta_node=True)
                if relation:
                    cls.add_to_class(field.name, relation)

                if settings.CONNECT_META_NODES:
                    relation = cls.get_related_node_property_for_field(field, meta_node=False)
                    if relation:
                        cls.add_to_class('_%s' % field.name, relation)

            # Add reverse relations
            elif field in reverse_relations:
                related_name = field.related_name or '%s_set' % field.name
                relation = cls.get_related_node_property_for_field(field, meta_node=True)
                if relation:
                    cls.add_to_class(related_name, relation)

                if settings.CONNECT_META_NODES:
                    relation = cls.get_related_node_property_for_field(field, meta_node=False)
                    if relation:
                        cls.add_to_class('_%s' % related_name, relation)

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        install_labels(cls, quiet=True, stdout=None)
        return cls


class MetaNodeMixin(ModelNodeMixin):
    """
    Mixin class for ``StructuredNode`` which adds a number of class methods
    in order to calculate relationship fields from a Django model class.
    """

    def __init__(self, *args, **kwargs):
        self._instance = self.__class__.Meta.model
        self.__recursion_depth__ = 0

        defaults = {key: getattr(self._instance._meta, key, kwargs.get(key, None))
                    for key, _ in self.__all_properties__}
        kwargs.update(defaults)
        StructuredNode.__init__(self, *args, **kwargs)

        # FIXME: Don't look up against id if using inflate with a raw query.
        if not hasattr(self, 'id'):
            params = self.deflate(self.__properties__)

            # Remove any attributes we don't want to include in the MATCH query.
            exclude = ('model_permisssions', 'is_intermediary')
            for attr in exclude:
                if attr in params:
                    del params[attr]

            node_id = self._get_id_from_database(params)
            if node_id:
                self.id = node_id

    @timeit
    def recursive_connect(self, prop, relation, max_depth):
        """
        Recursively connect a related branch.
        :param prop: For example a ``ZeroOrMore`` instance.
        :param relation: ``RelationShipDefinition`` instance
        :param max_depth: Maximum depth of recursive connections to be made.
        :returns: None
        """
        from chemtrails.neoutils import get_meta_node_for_model

        @timeit
        def back_connect(n, depth):
            if n._recursion_depth >= depth:
                return
            n._recursion_depth += 1
            for p, r in n.defined_properties(aliases=False, properties=False).items():
                n.recursive_connect(getattr(n, p), r, max_depth=n._recursion_depth - 1)

        relations = prop.all()
        klass = relation.definition['node_class']
        is_meta = relation.definition['model'].is_meta.default_value()
        if is_meta:
            node = get_meta_node_for_model(klass.Meta.model)
            if not node._is_bound:
                node.save()
            if node not in relations:
                prop.connect(node)
                self._log_relationship_definition('Connected', node, prop)
                back_connect(node, max_depth)
        elif not is_meta and settings.CONNECT_META_NODES:
            for node in relation.definition['node_class'].nodes.all():
                if node not in relations:
                    prop.connect(node)
                    self._log_relationship_definition('Connected', node, prop)
                    back_connect(node, max_depth)

    def sync(self, max_depth=1, update_existing=True, create_empty=False):
        """
        Synchronizes the current node with data from the database and
        connect all directly related nodes.
        :param max_depth: Maximum depth of recursive connections to be made.
        :param update_existing: If True, save data from the django model to graph node.
        :param create_empty: If the Node has no relational fields, don't create it.
        :returns: The ``MetaNode`` instance or None if not created.
        """
        cls = self.__class__

        if self._is_ignored:
            try:
                self.delete()
            except ValueError:
                pass
            finally:
                return None

        if not cls.has_relations and not create_empty:
            return None

        if update_existing:
            if not self._is_bound:
                node = cls.nodes.get_or_none(**{'app_label': self.app_label,
                                                'model_name': self.model_name})
                if node:
                    self.id = node.id

            # Make sure the neo4j node properties and relationships matches
            # the class definition.
            self.__update_raw_node__()

            # Finally save the node
            self.save()

        # Connect relations
        for prop, relation in self.defined_properties(aliases=False, properties=False).items():
            prop = getattr(self, prop)
            self.recursive_connect(prop, relation, max_depth=max_depth)
        return self
