# -*- coding: utf-8 -*-

from chemtrails.compat import rest_framework
assert rest_framework, ('chemtrails.contrib.permissions module requires '
                        'django-rest-framework to be installed. Install with '
                        '`pip install djangorestframework`.')

default_app_config = 'chemtrails.contrib.permissions.apps.ChemtrailsPermissionsConfig'
