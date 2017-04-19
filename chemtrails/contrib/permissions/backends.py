# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from django.db import models

from chemtrails.compat import is_authenticated
from chemtrails.contrib.permissions.utils import GraphPermissionChecker, check_permissions_app_label


class ChemoPermissionsBackend(ModelBackend):
    """
    Graph based permission backend for Django.
    """
    def authenticate(self, username=None, password=None, **kwargs):
        """
        This backend does not support authentication.
        """
        return None

    def has_perm(self, user_obj, perm, obj=None):
        """
        Returns ``True`` if given ``user_obj`` has ``perm`` for ``obj``. If
        no ``obj`` is given, return ``False``.
        """
        if not isinstance(obj, models.Model):
            return False

        if not is_authenticated(user_obj):
            return False

        if '.' in perm:
            check_permissions_app_label(perm)

        checker = GraphPermissionChecker(user_obj)
        return checker.has_perm(perm, obj)

    def get_all_permissions(self, user_obj, obj=None):
        """
        Returns a list of permission strings that the given ``user_obj`` has for ``obj``.
        """
        if not isinstance(obj, models.Model) or not is_authenticated(user_obj):
            return set()

        checker = GraphPermissionChecker(user_obj)
        return checker.get_perms(obj)
