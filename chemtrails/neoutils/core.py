# -*- coding: utf-8 -*-

import operator
from functools import reduce

from django.core.exceptions import ImproperlyConfigured
from django.db import models

from neomodel import *


field_property_map = {
    models.ForeignKey: RelationshipFrom,
    models.OneToOneField: RelationshipFrom,
    models.ManyToManyField: RelationshipFrom,

    models.AutoField: IntegerProperty,
    models.BigAutoField: IntegerProperty,
    models.BigIntegerField: IntegerProperty,
    models.BooleanField: BooleanProperty,
    models.CharField: StringProperty,
    models.CommaSeparatedIntegerField: ArrayProperty,  # TODO: Special
    models.DateField: DateProperty,
    models.DateTimeField: DateTimeProperty,
    models.DecimalField: FloatProperty,
    models.DurationField: StringProperty,
    models.EmailField: StringProperty,
    models.FilePathField: StringProperty,
    models.FileField: StringProperty,  # TODO: Special
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


class Meta(type):

    model = None

    def __new__(mcs, name, bases, attrs):
        cls = super(Meta, mcs).__new__(mcs, str(name), bases, attrs)
        return cls


class ModelMeta(NodeMeta):
    """
    Base Meta class for ``StructuredNode`` which adds a model class.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Create a mapping to hold related node fields
        cls.__related_nodes__ = ()

        # Store dynamic properties for internal calculations
        cls.__dynamic_properties__ = ()

        if getattr(cls, 'Meta', None):
            cls.Meta = Meta('Meta', (Meta,), dict(cls.Meta.__dict__))

            # A little hack which helps us dynamically create ModelRelation classes
            # where variables holding the model class is out of scope.
            if hasattr(cls, '__metaclass_model__') and not cls.Meta.model:
                cls.Meta.model = getattr(cls, '__metaclass_model__', None)
                delattr(cls, '__metaclass_model__')

            if not getattr(cls.Meta, 'model', None):
                raise ValueError('%s.Meta.model attribute cannot be None.' % name)

            setattr(cls, '__label__', '{object_name}RelationMeta'.format(
                object_name=cls.Meta.model._meta.object_name))

        elif not getattr(cls, '__abstract_node__', None):
            raise ImproperlyConfigured('%s must implement a Meta class.' % name)

        return cls


class ModelNodeMeta(ModelMeta):
    """
    Meta class for ``ModelNode``.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelNodeMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set label for node
        cls.__label__ = '{object_name}Node'.format(object_name=cls.Meta.model._meta.object_name)

        # Add properties for the class fields
        for field in cls.Meta.model._meta.get_fields():
            if field.__class__ in field_property_map:
                cls.__dynamic_properties__ += ((field.name if field is not cls._pk_field else 'pk',
                                                cls.get_property_class_for_field(field.__class__)),)

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        return cls


class ModelNodeMixin(object):
    """
    Mixin class for ``StructuredNode`` for dealing with Django model instances.
    """
    @classproperty
    def _pk_field(cls):
        model = cls.Meta.model
        pk_field = reduce(operator.eq,
                          filter(lambda field: field.primary_key, model._meta.fields))
        return pk_field

    @staticmethod
    def get_property_class_for_field(klass):
        """
        Returns the appropriate property class for field class.
        """
        if klass in field_property_map:
            return field_property_map[klass]
        return None

    @classmethod
    def get_model_string(cls):
        return '{app_label}.{model_name}'.format(app_label=cls.Meta.model._meta.app_label,
                                                 model_name=cls.Meta.model._meta.model_name)

    @classmethod
    def defined_properties(cls, aliases=True, properties=True, rels=True):
        from neomodel.relationship_manager import RelationshipDefinition

        props = super(ModelNodeMixin, cls).defined_properties(aliases, properties, rels)
        if hasattr(cls, '__dynamic_properties__'):
            for key, prop in cls.__dynamic_properties__:
                if ((aliases and isinstance(prop, AliasProperty))
                    or (properties and hasattr(prop, '__class__') and issubclass(prop.__class__, Property)
                        and not isinstance(prop, AliasProperty)) or
                        (rels and isinstance(prop, RelationshipDefinition))):
                    if not hasattr(cls, key):
                        setattr(cls, key, prop)
                    props[key] = prop
        return props

    @classmethod
    def create_or_update_one(cls, *props, **kwargs):
        """
        Call to MERGE with parameters map to create or update a single instance. A new instance
        will be created and saved if it does not already exists. If an instance already exists,
        all optional properties specified will be updated.
        :param props: List of dict arguments to get or create the entity with.
        :keyword relationship: Optional, relationship to get/create on when new entity is created.
        :keyword lazy: False by default, specify True to get node with id only without the parameters.
        :returns: A single ``StructuredNode` instance.
        """
        with db.transaction:
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

    @classmethod
    def sync(cls, instance, **kwargs):
        """
        Write instance node to the graph.
        :param instance: Django model instance.
        :param kwargs: Mapping of keyword arguments which will be passed to ``create_or_update_one()``
        :returns: The node instance or None.
        """
        defaults = {}
        for field in cls.Meta.model._meta.get_fields():
            value = getattr(instance, field.name, None)
            defaults[field.name if field is not cls._pk_field else 'pk'] = value
        result = cls.create_or_update_one([defaults], **kwargs)
        return result


class ModelRelationsMeta(ModelMeta):
    """
    Meta class for ``ModelRelationNode``.
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelRelationsMeta, mcs).__new__(mcs, str(name), bases, attrs)

        # Set label for node
        cls.__label__ = '{object_name}RelationMeta'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.uuid = UniqueIdProperty()
        cls.model = StringProperty(unique_index=True, default=cls.get_model_string)

        # Store dynamic relationships
        for relation in cls.get_relation_fields(cls.Meta.model):
            if hasattr(relation, 'field') and relation.field.__class__ in field_property_map:
                related_node, related_type = cls.get_node_property_for_field(relation.field)
                cls.__related_nodes__ += ((relation.name, related_node),)
                cls.__dynamic_properties__ += ((relation.name, related_type),)

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        return cls


class ModelRelationsMixin(ModelNodeMixin):
    """
    Mixin class for ``StructuredNode`` which adds a number of class methods
    in order to calculate relationship fields from a Django model class.
    """
    @classproperty
    def has_relations(cls):
        return len(cls.__related_nodes__) > 0

    @staticmethod
    def get_relation_fields(model):
        """
        Get a list of fields on the model which represents relations.
        """
        return [
            field for field in model._meta.get_fields()
            if field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)
        ]

    @classmethod
    def get_node_property_for_field(cls, field):
        """
        Instantiate and return the property for ``field``.
        """
        from chemtrails.neoutils import get_relations_node_class_for_model

        class DynamicRelation(StructuredRel):
            relation_type = StringProperty(default=field.__class__.__name__)
            remote_field = StringProperty(default=str(field.remote_field.field).lower())
            target_field = StringProperty(default=str(field.target_field).lower())

        prop = cls.get_property_class_for_field(field.__class__)

        RelatedNode = get_relations_node_class_for_model(field.remote_field.related_model)
        node = RelatedNode.create_or_update_one([{'model': cls.get_model_string()}])
        return node, prop(cls_name=RelatedNode, rel_type='RELATES_TO', model=DynamicRelation)

    @classmethod
    def sync(cls, create_empty=False, **kwargs):
        """
        Write node to the graph and create all relationships.
        :param create_empty: False by default. If True and no calculated relationships, write the
                             node to the graph anyway.
        :param kwargs: Mapping of keyword arguments which will be passed to ``create_or_update_one()``
        :returns: The node instance or None.
        """
        if not cls.has_relations and not create_empty:
            return None

        result = cls.create_or_update_one([{'uuid': cls.uuid.default_value()}], **kwargs)

        # Connect related nodes
        for attr, related_node in result.__related_nodes__:
            field = getattr(result, attr)
            field.connect(related_node)
        return result
