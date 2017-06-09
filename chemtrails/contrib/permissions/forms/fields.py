# -*- coding: utf-8 -*-

import json
from collections import defaultdict, OrderedDict

from django.core import exceptions
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chemtrails.contrib.permissions import forms


class JSONField(models.Field):
    empty_strings_allowed = False
    description = _('An ordered JSON object')
    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid JSON string.")
    }

    def __init__(self, *args, **kwargs):
        """
        :param dump_kwargs: Keyword arguments which will be passed to `json.dumps()`
        :param load_kwargs: Keyword arguments which will be passed to `json.loads()`
        """
        self.dump_kwargs = kwargs.pop('dump_kwargs', {
            'cls': DjangoJSONEncoder,
            'ensure_ascii': False,
            'sort_keys': False,
            'separators': (',', ':')
        })
        self.load_kwargs = kwargs.pop('load_kwargs', {
            'object_pairs_hook': OrderedDict
        })
        if not kwargs.get('null', False):
            kwargs['default'] = kwargs.get('default', defaultdict(OrderedDict))
        super(JSONField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'dump_kwargs': self.dump_kwargs,
            'load_kwargs': self.load_kwargs,
            'form_class': forms.JSONFormField,
            'widget': forms.JSONWidget
        }
        return super(JSONField, self).formfield(**defaults)

    def from_db_value(self, value, *args, **kwargs):
        """
        Convert the JSON string to an OrderedDict.
        """
        if value is None:
            return None
        if isinstance(value, (dict, OrderedDict)):
            value = json.dumps(value, **self.dump_kwargs)
        return value

    def get_default(self):
        default = super(JSONField, self).get_default()
        if default and isinstance(default, (dict, OrderedDict)):
            return json.dumps(default, **self.dump_kwargs)
        return default

    def get_db_prep_value(self, value, connection, prepared=False):
        return self.get_prep_value(value)

    def get_internal_type(self):
        return "TextField"

    def get_prep_value(self, value):
        """
        Convert the value to a JSON string ready to
        be stored in the database.
        """
        if value is None:
            if not self.null and self.blank:
                return ''
            return None
        return self.value_to_string(value)

    def to_python(self, value):
        return self.value_to_string(value)

    def validate(self, value, model_instance):
        if not self.null and value is None:
            raise exceptions.ValidationError(self.error_messages['null'])
        try:
            self.get_prep_value(value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError(self.error_messages['invalid'],
                                             code='invalid', params={'value': value})

    def value_to_string(self, value):
        if isinstance(value, (dict, OrderedDict)):
            value = json.dumps(value, **self.dump_kwargs)
        return json.dumps(json.loads(value, **self.load_kwargs), **self.dump_kwargs)
