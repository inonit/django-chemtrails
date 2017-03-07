# -*- coding: utf-8 -*-

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe


class GraphWidget(forms.Widget):
    """
    Django admin widget for rendering a Neo4j graph.
    """

    template = 'admin/chemtrails/permissions/graph_widget.html'

    class Media:
        js = ('https://cdnjs.cloudflare.com/ajax/libs/react/15.4.2/react.min.js',)

    def render(self, name, value, attrs=None):
        return mark_safe(
            render_to_string(self.template, context={})
        )
