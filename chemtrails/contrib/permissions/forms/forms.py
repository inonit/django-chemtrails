# -*- coding: utf-8 -*-

import json

from django import forms
from django.utils.translation import ugettext_lazy as _
# from chemtrails.contrib.permissions.forms.widgets import GraphWidget
# from chemtrails.contrib.permissions.models import AccessRule


# class GraphField(forms.Field):
#     """
#     A Field which will render a GraphWidget.
#     """
#     widget = GraphWidget
#
#
# class AccessRuleForm(forms.ModelForm):
#
#     graph = GraphField(required=False, label='')
#
#     class Meta:
#         model = AccessRule
#         fields = '__all__'


class JSONFieldForm(forms.CharField):
    default_error_messages = {
        'invalid': _("'%(value)s' value must be valid JSON."),
    }

    def __init__(self, **kwargs):
        kwargs.setdefault('widget', forms.Textarea)
        self.dump_kwargs = kwargs.pop('dump_kwargs', {})
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        super(JSONFieldForm, self).__init__(**kwargs)

    def to_python(self, value):
        if self.disabled:
            return value
        if value in self.empty_values:
            return None
        try:
            if value and isinstance(value, str):
                value = json.loads(value, **self.load_kwargs)
            return value
        except ValueError:
            raise forms.ValidationError(self.error_messages['invalid'],
                                        code='invalid', params={'value': value})

    def bound_data(self, data, initial):
        if self.disabled:
            return initial
        try:
            return json.loads(data, **self.load_kwargs)
        except ValueError as e:
            return str(data)

    def prepare_value(self, value):
        if isinstance(value, str):
            return value
        return json.dumps(value, **self.dump_kwargs)
