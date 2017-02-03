# -*- coding: utf-8 -*-

from django.db import models
from neomodel import *


class ModelRelationWrapper(object):

    field_property_map = {
        models.ForeignKey: (RelationshipTo, ZeroOrOne),
        models.OneToOneField: (RelationshipTo, ZeroOrOne),
        models.ManyToManyField: (RelationshipTo, ZeroOrMore),
    }

    def __init__(self, model):
        self.model = model

    @staticmethod
    def get_relation_fields(model):
        """
        Get a list of fields on the model which represents relations.
        """
        return [
            field for field in model._meta.get_fields()
            if field.is_relation or field.one_to_one or (field.many_to_one and field.related_model)
        ]

    def get_node_class(self):
        """
        Returns a `DynamicNode` class suitable for storing relation meta
        data about ``self.model``.
        """
        class DynamicNode(StructuredNode):
            __label__ = '{object_name}RelationMeta'.format(object_name=self.model._meta.object_name)
            uuid = UniqueIdProperty()
            content_type = StringProperty(unique_index=True,
                                          default='{app_label}.{model}'.format(app_label=self.model._meta.app_label,
                                                                               model=self.model._meta.model_name))

            def __init__(self, *args, **kwargs):
                self.__all_relationships__ = tuple(
                    DynamicNode.defined_properties(aliases=False, properties=False).items())
                super(DynamicNode, self).__init__(*args, **kwargs)

            @property
            def label(cls):
                return cls.__label__

        for relation in self.get_relation_fields(self.model):
            if hasattr(relation, 'field') and relation.field.__class__ in self.field_property_map:
                setattr(DynamicNode, relation.name, self.get_property_for_field(relation.field))

        return DynamicNode

    def get_property_class_for_field(self, klass):
        """
        Returns the appropriate property class for field class.
        """
        if klass in self.field_property_map:
            return self.field_property_map[klass]
        return None

    def get_property_for_field(self, field):
        """
        Instantiate and return the property for ``field``.
        """
        class DynamicRelation(StructuredRel):
            remote_field = StringProperty(default=str(field.remote_field.field).lower())
            target_field = StringProperty(default=str(field.target_field).lower())

        prop, cardinality = self.get_property_class_for_field(field.__class__)
        related_node = ModelRelationWrapper(field.remote_field.related_model).get_node_class()
        return prop(cls_name=related_node, rel_type='RELATES_THROUGH', cardinality=cardinality, model=DynamicRelation)

    def save(self):
        """
        Save the model as a node representation in the graph and return it.
        """
        DynamicNode = self.get_node_class()

        try:
            node = DynamicNode.nodes.get(content_type='{app_label}.{model}'.format(
                app_label=self.model._meta.app_label, model=self.model._meta.model_name))
        except DynamicNode.DoesNotExist:
            node = DynamicNode()

        node.save()
        return node



