# -*- coding: utf-8 -*-

import ast
import functools
import logging
import os
import time
from collections import Sequence

logger = logging.getLogger(__name__)


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


def timeit(func):
    """
    Decorator which logs the timing of executing a function
    or method call to DEBUG logger.
    """
    @functools.wraps(func)
    def f(*args, **kwargs):
        timestamp = time.time()
        func(*args, **kwargs)
        logger.debug('function [{0}] executed in {1}s'.format(
            f.__name__, '%.5f' % (time.time() - timestamp)
        ))
    return f


def get_environment_variable(name, fallback=None):
    """
    Get environment variable and try to cast it to proper python type.
    :param name: Environment variable name to look for.
    :param fallback: Default fallback value if ``name`` is not found.
    :returns: Environment variable value if found, else None.
    """
    value = os.environ.get(name, fallback)
    try:
        if value in ('true', 'TRUE', 'false', 'FALSE'):
            value = value.capitalize()
        value = ast.literal_eval(value)
    except ValueError:
        pass
    return value

