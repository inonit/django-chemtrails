# -*- coding: utf-8 -*-

import operator
from functools import reduce

from django.core.exceptions import ImproperlyConfigured, ValidationError
from django.db import models

from neomodel import *


field_property_map = {
    models.ForeignKey: RelationshipFrom,
    models.OneToOneField: RelationshipFrom,
    models.ManyToManyField: RelationshipFrom,
    models.ManyToOneRel: RelationshipTo,
    models.OneToOneRel: RelationshipTo,
    models.ManyToManyRel: RelationshipTo,

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


class ModelProperty(Property):

    def normalize(self, value):
        return repr(value)


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

        # Create a tuple to hold related node fields
        cls.__related_nodes__ = ()

        if getattr(cls, 'Meta', None):
            cls.Meta = Meta('Meta', (Meta,), dict(cls.Meta.__dict__))

            # A little hack which helps us dynamically create ModelNode classes
            # where variables holding the model class is out of scope.
            if hasattr(cls, '__metaclass_model__') and not cls.Meta.model:
                cls.Meta.model = getattr(cls, '__metaclass_model__', None)
                delattr(cls, '__metaclass_model__')

            if not getattr(cls.Meta, 'model', None):
                raise ValueError('%s.Meta.model attribute cannot be None.' % name)

            setattr(cls, '__label__', '{object_name}Meta'.format(object_name=cls.Meta.model._meta.object_name))

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

        cls.__related_nodes__ = {
            'forward': (),
            'reverse': ()
        }

        forward_relations = cls.get_forward_relation_fields()
        reverse_relations = cls.get_reverse_relation_fields()

        # Add some default fields
        cls.pk = cls.get_property_class_for_field(cls._pk_field.__class__)(unique_index=True)

        for field in cls.Meta.model._meta.get_fields():

            # Add forward relations
            if field in forward_relations:
                node, relationship = cls.get_related_node_property_for_field(field)
                setattr(cls, field.name, relationship)
                cls.__related_nodes__['forward'] += ((field.name, node),)

            # Add reverse relations
            elif field in reverse_relations:
                related_name = field.related_name or '%s_set' % field.name
                node, relationship = cls.get_related_node_property_for_field(field.field)
                setattr(cls, related_name, relationship)
                cls.__related_nodes__['reverse'] += ((related_name, node),)

            # Add concrete fields
            else:
                if field is not cls._pk_field:
                    setattr(cls, field.name, cls.get_property_class_for_field(field.__class__)())

        # relations = cls.get_relation_fields(cls.Meta.model)
        # for field in cls.Meta.model._meta.get_fields():
        #     if field in relations and hasattr(field, 'field') and field.field.__class__ in field_property_map:
        #         related_node, related_type = cls.get_related_node_property_for_field(field.field)
        #         setattr(cls, field.name, related_type)
        #         cls.__related_nodes__ += ((field.name, related_node),)
        #     elif field is not cls._pk_field:
        #         prop = cls.get_property_class_for_field(field.__class__)
        #         setattr(cls, field.name, cls.get_property_class_for_field(field.__class__)())

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

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
    def get_related_node_property_for_model(cls, model):
        """
        Instantiate and return the property for ``model``.
        """
        from chemtrails.neoutils import get_relations_node_class_for_model

        class DynamicRelation(StructuredRel):
            # relation_type = StringProperty(default=field.__class__.__name__)
            # remote_field = StringProperty(default=str(field.remote_field.field).lower())
            # target_field = StringProperty(default=str(field.target_field).lower())
            pass

        RelatedNode = get_relations_node_class_for_model(model)
        node = RelatedNode.create_or_update_one([{'model': cls.get_model_string()}])
        return node, RelationshipTo(cls_name=RelatedNode, rel_type='TYPE_OF', model=DynamicRelation)

    @classmethod
    def get_related_node_property_for_field(cls, field):
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

    # instance = ModelProperty()  # FIXME: Crashes without this.. why?

    def __init__(self, instance=None, *args, **kwargs):
        self.instance = instance
        for key, _ in self.__all_properties__:
            kwargs[key] = getattr(self.instance, key, kwargs.get(key, None))
        super(ModelNodeMixin, self).__init__(self, *args, **kwargs)

    def full_clean(self, exclude=None, validate_unique=True):
        exclude = exclude or []

        props = self.__properties__
        for key in exclude:
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
        self.full_clean(exclude=['instance'], validate_unique=not update_existing)

        # For now, we assume that `pk` field always is unique for the node type
        cls = self.__class__
        node = cls.nodes.get_or_none(**{'pk': self.pk})

        if node and update_existing:
            # If node is found, update with current attributes and save.
            # TODO: Should probably be other way around
            node_props = node.__class__.defined_properties(aliases=False, rels=False)
            for attr, prop in cls.defined_properties(aliases=False, rels=False).items():
                db_property = prop.db_property or attr
                if db_property in node_props:
                    setattr(node, db_property, prop.inflate(getattr(self, attr)))
            node.save()
            return node

        return self.save()


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

        # Add relations for the model
        for relation in cls.get_relation_fields(cls.Meta.model):
            if hasattr(relation, 'field') and relation.field.__class__ in field_property_map:
                related_node, related_type = cls.get_related_node_property_for_field(relation.field)
                cls.__related_nodes__ += ((relation.name, related_node),)
                setattr(cls, relation.name, related_type)

        # Recalculate definitions
        cls.__all_properties__ = tuple(cls.defined_properties(aliases=False, rels=False).items())
        cls.__all_aliases__ = tuple(cls.defined_properties(properties=False, rels=False).items())
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        return cls


class ModelRelationsMixin(ModelNodeBase):
    """
    Mixin class for ``StructuredNode`` which adds a number of class methods
    in order to calculate relationship fields from a Django model class.
    """
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
