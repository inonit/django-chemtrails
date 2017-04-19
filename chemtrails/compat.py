# -*- coding: utf-8 -*-

import django

# Support Django REST Framework
try:
    import rest_framework
except ImportError:
    rest_framework = None


# Django 1.10 compatibility
def is_authenticated(user):
    if django.VERSION < (1, 10):
        return user.is_authenticated()
    return user.is_authenticated
