# -*- coding: utf-8 -*-

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db import models
from django.utils import six

from neomodel import *


field_property_map = {
    models.ForeignKey: (RelationshipTo, ZeroOrOne),
    models.OneToOneField: (RelationshipTo, ZeroOrOne),
    models.ManyToManyField: (RelationshipTo, ZeroOrMore),
}


class Meta(type):

    model = None

    def __new__(mcs, name, bases, attrs):
        cls = super(Meta, mcs).__new__(mcs, str(name), bases, attrs)
        return cls


class ModelRelationsMeta(NodeMeta):
    """
    Meta class for ModelRelationNode
    """
    def __new__(mcs, name, bases, attrs):
        cls = super(ModelRelationsMeta, mcs).__new__(mcs, str(name), bases, attrs)

        if getattr(cls, 'Meta', None):
            cls.Meta = Meta('Meta', (Meta,), dict(cls.Meta.__dict__))

            if not hasattr(cls.Meta, 'model'):
                raise AttributeError('%s.Meta is missing a model attribute.' % name)

            elif hasattr(cls.Meta, 'model') and not cls.Meta.model:
                raise AttributeError('Model.meta attribute cannot be None.')

            setattr(cls, '__label__', '{object_name}RelationMeta'.format(
                object_name=cls.Meta.model._meta.object_name))

        elif not getattr(cls, '__abstract_node__', None):
            raise ImproperlyConfigured('%s must implement a Meta class.' % name)

        # Set label for node
        cls.__label__ = '{object_name}RelationMeta'.format(object_name=cls.Meta.model._meta.object_name)

        # Add some default fields
        cls.uuid = UniqueIdProperty()
        cls.content_type = StringProperty(unique_index=True, default=cls.get_ctype_name)

        # Add relations for the model
        for relation in cls.get_relation_fields(cls.Meta.model):
            if hasattr(relation, 'field') and relation.field.__class__ in field_property_map:
                related_node, relation_property = cls.get_property_for_field(relation.field)
                cls.related_nodes[relation.name] = related_node
                setattr(cls, relation.name, relation_property)

        # Recalculate relations
        cls.__all_relationships__ = tuple(cls.defined_properties(aliases=False, properties=False).items())

        return cls


class ModelRelationsMixin(object):

    related_nodes = {

    }

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
    def get_ctype_name(cls):
        return '{app_label}.{model_name}'.format(app_label=cls.Meta.model._meta.app_label,
                                                 model_name=cls.Meta.model._meta.model_name)

    @classmethod
    def get_property_for_field(cls, field):
        """
        Instantiate and return the property for ``field``.
        """

        class DynamicRelation(StructuredRel):
            remote_field = StringProperty(default=str(field.remote_field.field).lower())
            target_field = StringProperty(default=str(field.target_field).lower())

        prop, cardinality = cls.get_property_class_for_field(field.__class__)

        @six.add_metaclass(ModelRelationsMeta)
        class RelatedNode(ModelRelationsMixin, StructuredNode):
            class Meta:
                model = field.remote_field.related_model

        nodes = RelatedNode.create_or_update([
            {'content_type': cls.get_ctype_name()}
        ])
        return nodes[0], prop(cls_name=RelatedNode, rel_type='RELATES_THROUGH', model=DynamicRelation)

    @hooks
    def save(self):
        super(ModelRelationsMixin, self).save()

        # Connect related nodes
        for attr, node in self.related_nodes.items():
            field = getattr(self, attr)
            field.connect(node)

        return self


# TODO: Make a base class we can instantiate!
# @six.add_metaclass(ModelRelationsMeta)
# class ModelRelationsNode(StructuredNode):
#     class Meta:
#         model = None

