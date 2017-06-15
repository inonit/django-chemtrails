# -*- coding: utf-8 -*-

from collections import OrderedDict

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.utils import six
from django.utils.translation import ugettext_lazy as _

from neomodel import properties
from neomodel.cardinality import One
from neomodel.relationship import RelationshipMeta

from rest_framework import serializers

from chemtrails.contrib.permissions.models import AccessRule

_field_mapping = {
    properties.AliasProperty: lambda prop: _field_mapping[prop.target],
    properties.ArrayProperty: serializers.ListField,
    properties.BooleanProperty: serializers.BooleanField,
    properties.DateProperty: serializers.DateField,
    properties.DateTimeProperty: serializers.DateTimeField,
    properties.EmailProperty: serializers.EmailField,
    properties.FloatProperty: serializers.FloatField,
    properties.IntegerProperty: serializers.IntegerField,
    properties.JSONProperty: serializers.JSONField,
    properties.RegexProperty: serializers.RegexField,
    properties.StringProperty: serializers.CharField,
    properties.UniqueIdProperty: serializers.UUIDField
}


class RelationshipSerializer(serializers.Serializer):
    """
    REST Framework based Serializer which dynamically
    serializes a ``StructuredRel`` instance.
    """
    def get_fields(self):
        field_mapping = OrderedDict()
        for key, value in self.instance.items():
            if key == 'node_class':
                field_mapping['to'] = serializers.CharField(default=value.__label__)
            elif isinstance(value, RelationshipMeta):
                field_mapping['meta'] = serializers.DictField(
                    child=serializers.CharField(),
                    default={k: v.default for k, v in value.__dict__.items() if isinstance(v, properties.Property)})
            elif key == 'direction':
                field_mapping[key] = serializers.IntegerField(default=value)
            elif key == 'relation_type':
                field_mapping[key] = serializers.CharField(default=value)
        return field_mapping


class NodeSerializer(serializers.Serializer):
    """
    REST Framework based Serializer which dynamically
    serializes a ``StructuredNode`` instance.
    """
    def get_fields(self):
        field_mapping = OrderedDict()

        # Normal properties
        for field, property_class in self.instance.defined_properties(aliases=False, rels=False).items():
            # TODO: Support AliasField - check for __call__ in _field_mapping.
            field_mapping['id'] = serializers.IntegerField(default=self.instance.id)
            field_mapping['label'] = serializers.CharField(default=self.instance.__label__)
            field_mapping.update({
                field: self.get_serializer_field(property_class, **self._get_default_field_kwargs(property_class))
            })

        # Relationships
        for field, property_class in self.instance.defined_properties(aliases=False, properties=False).items():
            field_mapping.update({
                field: RelationshipSerializer(property_class.definition, many=not isinstance(property_class, One))
            })

        return field_mapping
    
    @staticmethod
    def _get_default_field_kwargs(property_class):
        """
        Return default kwargs used to initialize
        the Serializer field with.
        :param property_class: Neomodel property class
        """
        defaults = property_class.__dict__.copy()
        delete_attrs = [
            'db_property',
            'choices',
            'has_default',
            'index',
            'unique_index'
        ]
        for attr in delete_attrs:
            if attr in defaults:
                del defaults[attr]

        return defaults
    
    def get_serializer_field(self, property_class, **kwargs):
        """
        Returns the Serializer field instance that should be
        used for validating and deserializing the field.
        :param property_class: Neomodel property class.
        :param kwargs: Mapping with options used to initialize the Serializer field instance.
        """
        field = _field_mapping[property_class.__class__]
        return field(**kwargs)


class ContentTypeIdentityField(serializers.RelatedField):
    """
    REST Framework related field for ContentType objects.
    This field represents related ContentType objects by their natural key.
    """
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid content type "{ctype}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected content type string identifier, received {data_type}.'),
        'incorrect_length': _('Incorrect length. Expected content type string, '
                              'separated by punctuation. Received "{data}".')
    }

    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            self.fail('incorrect_type', data_type=type(data).__name__)

        try:
            app_label, model = data.split('.', 1)
            return ContentType.objects.get_by_natural_key(app_label=app_label, model=model)
        except ContentType.DoesNotExist:
            self.fail('does_not_exist', ctype=data)
        except ValueError:
            self.fail('incorrect_length', data=data)

    def to_representation(self, value):
        return '{app_label}.{model}'.format(app_label=value.app_label, model=value.model)


class PermissionIdentityField(serializers.RelatedField):
    """
    REST Framework related field for Permission objects.
    This field represents related Permission objects by their natural key.
    """
    default_error_messages = {
        'required': _('This field is required.'),
        'does_not_exist': _('Invalid permission "{data}" - object does not exist.'),
        'incorrect_type': _('Incorrect type. Expected permission string identifier, received {data_type}.'),
        'incorrect_length': _('Incorrect length. Expected permission string identifier, '
                              'separated by punctuation. Received "{data}".')
    }

    def to_internal_value(self, data):
        if not isinstance(data, six.text_type):
            self.fail('incorrect_type', data_type=type(data).__name__)

        try:
            app_label, codename = data.split('.', 1)
            return Permission.objects.select_related('content_type').get(
                codename=codename, content_type=ContentType.objects.get(app_label=app_label,
                                                                        permission__codename=codename))
        except (Permission.DoesNotExist, ContentType.DoesNotExist):
            self.fail('does_not_exist', data=data)
        except ValueError:
            self.fail('incorrect_length', data=data)

    def to_representation(self, value):
        codename, app_label, _ = value.natural_key()
        return '{app_label}.{codename}'.format(app_label=app_label, codename=codename)


class AccessRuleSerializer(serializers.ModelSerializer):
    """
    REST Framework Serializer for AccessRule objects.
    """
    ctype_source = ContentTypeIdentityField(queryset=ContentType.objects.all(), required=True)
    ctype_target = ContentTypeIdentityField(queryset=ContentType.objects.all(), required=True)
    permissions = PermissionIdentityField(queryset=Permission.objects.all(), many=True)
    relation_types = serializers.ListField(child=serializers.JSONField())

    class Meta:
        model = AccessRule
        fields = '__all__'
        read_only_fields = ('created', 'updated')
