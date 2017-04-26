# -*- coding: utf-8 -*-

from django.conf import settings

from rest_framework.filters import BaseFilterBackend


class ChemoPermissionsFilter(BaseFilterBackend):
    """
    A filter backend that limits results to those where the 
    requesting user has read object level permissions based on a
    calculated graph path.
    """
    perm_format = '%(app_label)s.view_%(model_name)s'

    def __init__(self):
        assert 'chemtrails.contrib.permissions' in settings.INSTALLED_APPS, (
            'Using %(class)s, but "chemtrails.contrib.permissions" not found in '
            'INSTALLED_APPS.' % {'class': self.__class__.__name__}
        )

    def filter_queryset(self, request, queryset, view):
        from chemtrails.contrib.permissions.utils import get_objects_for_user

        permission = self.perm_format % {
            'app_label': queryset.model._meta.app_label,
            'model_name': queryset.model._meta.model_name
        }
        return get_objects_for_user(request.user, permissions=permission, klass=queryset)
