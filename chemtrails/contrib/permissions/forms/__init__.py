# -*- coding: utf-8 -*-

from django import forms
from chemtrails.contrib.permissions.forms.widgets import GraphWidget
from chemtrails.contrib.permissions.models import AccessRule


class GraphField(forms.Field):
    """
    A Field which will render a GraphWidget.
    """
    widget = GraphWidget


class AccessRuleForm(forms.ModelForm):

    graph = GraphField(required=False, label='')

    class Meta:
        model = AccessRule
        fields = '__all__'
