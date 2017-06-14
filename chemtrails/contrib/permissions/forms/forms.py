# -*- coding: utf-8 -*-

import json

from django import forms
from django.utils.translation import ugettext_lazy as _
from chemtrails.contrib.permissions.forms.widgets import GraphWidget, JSONWidget
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
#     # graph = GraphField(required=False, label='')
#
#     class Meta:
#         model = AccessRule
#         fields = '__all__'


class JSONFormField(forms.CharField):
    default_error_messages = {
        'invalid': _("'%(value)s' is not a valid JSON string. JSON decode error: %(error)s")
    }

    def __init__(self, **kwargs):
        kwargs.setdefault('widget', JSONWidget)
        self.dump_kwargs = kwargs.pop('dump_kwargs', {})
        self.load_kwargs = kwargs.pop('load_kwargs', {})
        super(JSONFormField, self).__init__(**kwargs)

    def to_python(self, value):
        if self.disabled:
            return value
        if value in self.empty_values:
            return None
        try:
            if value and isinstance(value, str):
                value = json.dumps(json.loads(value, **self.load_kwargs), **self.dump_kwargs)
            return value
        except ValueError as e:
            raise forms.ValidationError(self.error_messages['invalid'],
                                        code='invalid', params={'value': value, 'error': str(e.args[0])})
