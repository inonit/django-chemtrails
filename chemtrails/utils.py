# -*- coding: utf-8 -*-

from neomodel import *


class NeoModelWrapper(object):
    """
    Something clever!
    """
    def __init__(self, instance):
        self.instance = instance

    def __repr__(self):
        """
        Return the NeoModel instance representation for this model
        """
        return self.instance

    def get_relation_fields(self):
        return [
            (f, f.model if f.model != self.instance else None)
            for f in self.instance._meta.get_fields()
            if f.is_relation or f.one_to_one or (f.many_to_one and f.related_model)
        ]

    def get_neo_model(self):

        class ModelNode(StructuredNode):
            pass

        for f, model in self.get_relation_fields():
            setattr(ModelNode, 'someinteger', IntegerProperty())

        instance = ModelNode()
        return instance
