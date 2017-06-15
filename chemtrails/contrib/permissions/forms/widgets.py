# -*- coding: utf-8 -*-
import json
from collections import OrderedDict

from django import forms
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

from neomodel import config


class GraphWidget(forms.Widget):
    """
    Django admin widget for rendering a Neo4j graph.
    """

    template = 'admin/chemtrails/contrib/permissions/graph_widget.html'

    class Media:
        js = (
            'https://cdnjs.cloudflare.com/ajax/libs/react/15.4.2/react.min.js',
            'chemtrails/contrib/permissions/js/main.js'
        )
        css = {
            'all': (
                'chemtrails/contrib/permissions/css/graph-widget.css',
                'https://cdnjs.cloudflare.com/ajax/libs/semantic-ui/2.2.9/semantic.min.css',)
        }

    def render(self, name, value, attrs=None):
        context = {
            'INITIAL_STATE': json.dumps({
                'settings': {
                    'baseUrl': 'localhost',
                    'neo4jUrl': config.DATABASE_URL
                },
            })
        }
        return mark_safe(
            render_to_string(self.template, context=context)
        )


class JSONWidget(forms.Textarea):
    """
    A simple text widget for displaying JSON strings.
    """
    def render(self, name, value, attrs=None):
        if not value:
            value = ''
        if value and isinstance(value, str):
            value = json.dumps(json.loads(value, object_pairs_hook=OrderedDict),
                               ensure_ascii=False, indent=2, sort_keys=False, separators=(',', ':'))
        return super(JSONWidget, self).render(name, value, attrs)
