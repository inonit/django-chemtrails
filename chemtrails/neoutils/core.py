# -*- coding: utf-8 -*-

import operator
from functools import reduce

from django.apps import apps
from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models
from django.db.models import Manager
from django.db.models.options import Options

from neomodel import *


field_property_map = {
    models.ForeignKey: RelationshipTo,
    models.OneToOneField: Relationship,
    models.ManyToManyField: RelationshipTo,
    models.ManyToOneRel: RelationshipFrom,
    models.OneToOneRel: RelationshipFrom,
    models.ManyToManyRel: RelationshipFrom,

    models.AutoField: IntegerProperty,
    models.BigAutoField: IntegerProperty,
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
    models.UUIDField: StringProperty
}


def get_model_string(model):
    """
    :param model: model
    :returns: <app_label>.<model_name> string representation for the model
    """
    return "{app_label}.{model_name}".format(app_label=model._meta.app_label, model_name=model._meta.model_name)


class Meta(type):
    """
    Meta class template.
    """
    model = None

    def __new__(mcs, name, bases, attrs):
        cls = super(Meta, mcs).__new__(mcs, str(name), bases, attrs)
        return cls


class NodeBase(NodeMeta):
    """
    Base Meta class for ``StructuredNode`` which adds a model class.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(NodeBase, mcs).__new__(mcs, str(name), bases, attrs)

        cls.__cache__ = {}
        if getattr(cls, 'Meta', None):
            cls.add_to_class('Meta', Meta('Meta', (Meta,), dict(cls.Meta.__dict__)))

            # A little hack which helps us dynamically create ModelNode classes
            # where variables holding the model class is out of scope.
            if hasattr(cls, '__metaclass_model__') and not cls.Meta.model:
                cls.Meta.model = getattr(cls, '__metaclass_model__', None)
                delattr(cls, '__metaclass_model__')

            if not getattr(cls.Meta, 'model', None):
                raise ValueError('%s.Meta.model attribute cannot be None.' % name)

        elif not getattr(cls, '__abstract_node__', None):
            raise ImproperlyConfigured('%s must implement a Meta class.' % name)

        return cls

    def add_to_class(cls, name, value):
        setattr(cls, name, value)


class ModelNodeMeta(NodeBase):
    """
    Meta class for ``ModelNode``.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelNodeMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set label for node
        cls.__label__ = '{object_name}Node'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.pk = cls.get_property_class_for_field(cls._pk_field.__class__)(unique_index=True)
        cls.model = StringProperty(default=get_model_string(cls.Meta.model))

        forward_relations = cls.get_forward_relation_fields()
        reverse_relations = cls.get_reverse_relation_fields()

        for field in cls.Meta.model._meta.get_fields():

            # Add forward relations
            if field in forward_relations:
                # node, relationship = cls.get_related_meta_node_property_for_field(field)
                # cls.__cache__[field.name] = node
                # setattr(cls, field.name, relationship)

                # TODO: Figure out how to avoid infinity loops on self referencing fields.
                if hasattr(field, 'to') and field.to == cls.Meta.model:
                    continue
                relationship = cls.get_related_node_property_for_field(field)
                cls.add_to_class(field.name, relationship)

            # Add reverse relations
            elif field in reverse_relations:
                # TODO: Figure out how to avoid infinity loops on reverse relations
                if hasattr(field, 'to') and field.to == cls.Meta.model:
                    continue
                related_name = field.related_name or '%s_set' % field.name
                relationship = cls.get_related_node_property_for_field(field)
                cls.add_to_class(related_name, relationship)

                # node, relationship = cls.get_related_meta_node_property_for_field(field)
                # cls.__cache__[related_name] = node
                # setattr(cls, related_name, relationship)

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


class ModelNodeBase(object):
    """
    Mixin class for ``StructuredNode`` for dealing with Django model instances.
    """
    @classproperty
    def _pk_field(cls):
        model = cls.Meta.model
        pk_field = reduce(operator.eq,
                          filter(lambda field: field.primary_key, model._meta.fields))
        return pk_field

    @classproperty
    def _cache(cls):
        """
        Return all cached values.
        """
        return cls.__cache__

    @classproperty
    def has_relations(cls):
        return len(cls.__all_relationships__) > 0

    @staticmethod
    def get_relation_fields(model):
        """
        Get a list of fields on the model which represents relations.
        """
        return [
            field for field in model._meta.get_fields()
            if field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)
        ]

    @staticmethod
    def get_property_class_for_field(klass):
        """
        Returns the appropriate property class for field class.
        """
        if klass in field_property_map:
            return field_property_map[klass]
        return None

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
    def get_related_node_property_for_field(cls, field):
        from chemtrails.neoutils import get_node_class_for_model

        reverse_field = True if isinstance(field, (
            models.ManyToManyRel, models.ManyToOneRel, models.OneToOneRel)) else False

        class DynamicRelation(StructuredRel):
            relation_type = StringProperty(default=field.__class__.__name__)
            remote_field = StringProperty(default=str(field.remote_field if reverse_field
                                                      else field.remote_field.field).lower())
            target_field = StringProperty(default=str(field.target_field).lower())

        relationship_type = {
            Relationship: 'MUTUAL_RELATION',
            RelationshipTo: 'FORWARD_RELATION',
            RelationshipFrom: 'REVERSE_RELATION'
        }
        prop = cls.get_property_class_for_field(field.__class__)
        klass = get_node_class_for_model(field.related_model)
        return prop(cls_name=klass, rel_type=relationship_type[prop], model=DynamicRelation)

    @classmethod
    def create_or_update_one(cls, *props, **kwargs):
        """
        Call to MERGE with parameters map to create or update a single _instance. A new _instance
        will be created and saved if it does not already exists. If an _instance already exists,
        all optional properties specified will be updated.
        :param props: List of dict arguments to get or create the entity with.
        :keyword relationship: Optional, relationship to get/create on when new entity is created.
        :keyword lazy: False by default, specify True to get node with id only without the parameters.
        :returns: A single ``StructuredNode` _instance.
        """
        with db.transaction:
            # TODO: Rewrite using `cls.nodes.get()`
            result = cls.create_or_update(*props, **kwargs)
            if len(result) > 1:
                raise MultipleNodesReturned(
                    'sync() returned more than one {klass} - it returned {num}.'.format(
                        klass=cls.__class__.__name__, num=len(result)))
            elif not result:
                raise cls.DoesNotExist(
                    '{klass} was unable to sync - Did not receive any results.'.format(
                        klass=cls.__class__.__name__))

            # There should be exactly one node for each relation type.
            result = result[0]
        return result


class ModelNodeMixin(ModelNodeBase):

    def __init__(self, instance=None, *args, **kwargs):
        self._instance = instance
        for key, _ in self.__all_properties__:
            kwargs[key] = getattr(self._instance, key, kwargs.get(key, None))
        super(ModelNodeMixin, self).__init__(self, *args, **kwargs)

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
                unique_props = [attr for attr, prop in cls.defined_properties(aliases=False, rels=False).items()
                                if prop not in exclude and prop.unique_index]
                for key in unique_props:
                    value = self.deflate({key: props[key]}, self)[key]
                    node = cls.nodes.get_or_none(**{key: value})

                    # if exists and not this node
                    if node and node.id != getattr(self, 'id', None):
                        raise ValidationError({key, 'already exists'})

        except DeflateError as e:
            raise ValidationError({e.property_name: e.msg})
        except RequiredProperty as e:
            raise ValidationError({e.property_name: 'is required'})

    def sync(self, update_existing=True):
        from chemtrails.neoutils import get_node_for_object, get_node_class_for_model
        self.full_clean(validate_unique=not update_existing)

        cls = self.__class__
        node = cls.nodes.get_or_none(**{'pk': self.pk})

        # If found, steal the id. This will cause the existing node to
        # be saved with data from this _instance.
        if node and update_existing:
            self.id = node.id

        self.save()

        # Connect relations
        for field_name, _ in cls.defined_properties(aliases=False, properties=False).items():
            field = getattr(self, field_name)

            # TODO: Connect meta
            # field.connect(cls._cache[field.name])

            # Connect related nodes
            if self._instance and hasattr(self._instance, field.name):
                attr = getattr(self._instance, field.name)

                if isinstance(attr, models.Model):
                    node = get_node_for_object(attr).sync(update_existing=True)
                    field.connect(node)
                elif isinstance(attr, Manager):
                    klass = get_node_class_for_model(attr.model)
                    related_nodes = klass.nodes.filter(pk__in=list(attr.values_list('pk', flat=True)))
                    for n in related_nodes:
                        try:
                            field.connect(n)
                        except ValueError as e:
                            continue
                            # raise e
        return self


class ModelRelationsMeta(NodeBase):
    """
    Meta class for ``ModelRelationNode``.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelRelationsMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set label for node
        cls.__label__ = '{object_name}RelationMeta'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.model = StringProperty(unique_index=True, default=get_model_string(cls.Meta.model))

        # Add relations for the model
        for relation in cls.get_relation_fields(cls.Meta.model):
            if hasattr(relation, 'field') and relation.field.__class__ in field_property_map:
                node, relationship = cls.get_related_meta_node_property_for_field(relation.field)
                cls.__cache__[relation.name] = node
                setattr(cls, relation.name, relationship)

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        install_labels(cls, quiet=True, stdout=None)
        return cls


class ModelRelationsMixin(ModelNodeBase):
    """
    Mixin class for ``StructuredNode`` which adds a number of class methods
    in order to calculate relationship fields from a Django model class.
    """

    @classmethod
    def get_related_meta_node_property_for_field(cls, field):
        from chemtrails.neoutils import get_relations_node_class_for_model

        reverse_field = True if isinstance(field, (
            models.ManyToManyRel, models.ManyToOneRel, models.OneToOneRel)) else False

        class DynamicRelation(StructuredRel):
            reversed = BooleanProperty(default=reverse_field)
            relation_type = StringProperty(default=field.__class__.__name__)
            remote_field = StringProperty(default=str(field.remote_field if reverse_field
                                                      else field.remote_field.field).lower())
            target_field = StringProperty(default=str(field.target_field).lower())

        prop_class = cls.get_property_class_for_field(field.__class__)

        MetaNode = get_relations_node_class_for_model(field.remote_field.related_model)
        node = MetaNode.create_or_update_one([{'model': get_model_string(cls.Meta.model)}])
        return node, prop_class(cls_name=MetaNode, rel_type='META_RELATION', model=DynamicRelation)

    @classmethod
    def sync(cls, create_empty=False, **kwargs):
        """
        Write node to the graph and create all relationships.
        :param create_empty: False by default. If True and no calculated relationships, write the
                             node to the graph anyway.
        :param kwargs: Mapping of keyword arguments which will be passed to ``create_or_update_one()``
        :returns: The node _instance or None.
        """
        if not cls.has_relations and not create_empty:
            return None

        result = cls.create_or_update_one([{'model': get_model_string(cls.Meta.model)}], **kwargs)

        # Connect relations
        for field_name, _ in cls.defined_properties(aliases=False, properties=False).items():
            if field_name in cls._cache:
                field = getattr(result, field_name)
                field.connect(cls._cache[field.name])

        return result
