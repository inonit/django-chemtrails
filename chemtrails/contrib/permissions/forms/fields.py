# -*- coding: utf-8 -*-

import json
from collections import OrderedDict

from django.core import exceptions
from django.core.serializers.json import DjangoJSONEncoder
from django.db import models
from django.utils.translation import ugettext_lazy as _

from chemtrails.contrib.permissions import forms


class JSONField(models.TextField):
    empty_strings_allowed = False
    description = _('An ordered JSON object')
    default_error_messages = {
        'invalid': _('Value must be valid JSON.')
    }

    def __init__(self, *args, **kwargs):
        """
        :param dump_kwargs: Keyword arguments which will be passed to `json.dumps()`
        :param load_kwargs: Keyword arguments which will be passed to `json.loads()`
        """
        self.dump_kwargs = kwargs.pop('dump_kwargs', {
            'cls': DjangoJSONEncoder,
            'sort_keys': False,
            'separators': (',', ':')
        })
        self.load_kwargs = kwargs.pop('load_kwargs', {
            'object_pairs_hook': OrderedDict
        })
        super(JSONField, self).__init__(*args, **kwargs)

    def formfield(self, **kwargs):
        defaults = {
            'dump_kwargs': self.dump_kwargs,
            'load_kwargs': self.load_kwargs,
            'form_class': forms.JSONFieldForm
        }
        return super(JSONField, self).formfield(**defaults)

    def from_db_value(self, value, *args, **kwargs):
        if isinstance(value, str):
            value = json.loads(value, **self.load_kwargs)
        return value

    def get_display_value(self, value):
        defaults = {'indent': 2}
        defaults.update(self.dump_kwargs)
        return json.dumps(value, **defaults)

    def get_prep_value(self, value):
        if value is not None:
            value = json.dumps(value, **self.dump_kwargs)
        return value

    def to_python(self, value):
        if isinstance(value, str):
            value = json.loads(value, **self.load_kwargs)
        return value

    def validate(self, value, model_instance):
        super(JSONField, self).validate(value, model_instance)
        try:
            json.dumps(value, **self.dump_kwargs)
        except TypeError:
            raise exceptions.ValidationError(self.error_messages['invalid'],
                                             code='invalid', params={'value': value})

    def value_to_string(self, obj):
        return self.value_from_object(obj)

    def value_from_object(self, obj):
        value = super(JSONField, self).value_from_object(obj)
        return self.get_display_value(value)
