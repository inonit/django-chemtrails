# -*- coding: utf-8 -*-

import ast
from django.utils import six
from django.contrib.postgres.fields import ArrayField


class ArrayChoiceField(ArrayField):
    """
    A field that allows us to store an array of choices.

    Uses Django 1.9's postgres ArrayField.

    Example usage:

        CHOICES = (
            (['New York', 'Chicago', 'Boston'], 'Cities'),
            (['Volcanoes', 'Parrots'], 'Cool stuff')
        )
        my_choices = ArrayChoiceField(models.CharField(max_length=100, blank=True), blank=True,
                                      choices=CHOICES)
    """
    def to_python(self, value):
        if isinstance(value, six.string_types):
            # Assume we're deserializing
            vals = ast.literal_eval(value)
            value = [self.base_field.to_python(val) for val in vals]
        return value
