# -*- coding: utf-8 -*-

from collections import Sequence


def get_model_string(model):
    """
    :param model: model
    :returns: <app_label>.<model_name> string representation for the model
    """
    return "{app_label}.{model_name}".format(app_label=model._meta.app_label, model_name=model._meta.model_name)


def flatten(sequence):
    """
    Flatten an arbitrary nested sequence.
    Example usage:
      >> my_list = list(flatten(nested_lists))
    :param sequence: A nested list or tuple.
    :returns: A generator with all values in a flat structure.
    """
    for i in sequence:
        if isinstance(i, Sequence) and not isinstance(i, (str, bytes)):
            yield from flatten(i)
        else:
            yield i
