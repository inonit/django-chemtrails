# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend

from chemtrails.contrib.permissions.core import GraphPermissionChecker
from chemtrails.contrib.permissions.utils import check_permissions_app_label


class ChemoPermissionsBackend(ModelBackend):
    """
    Graph based permission backend for Django.
    """

    def authenticate(self, username=None, password=None, **kwargs):
        return False

    def has_perm(self, user_obj, perm, obj=None):
        if '.' in perm:
            check_permissions_app_label(perm, obj)

        checker = GraphPermissionChecker(user_obj)
        return checker.has_perm(perm, obj)

    def get_all_permissions(self, user_obj, obj=None):
        checker = GraphPermissionChecker(user_obj)
        return checker.get_perms(obj)
