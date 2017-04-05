# -*- coding: utf-8 -*-

from django.contrib.auth.backends import ModelBackend
from django.contrib.contenttypes.models import ContentType

from chemtrails.contrib.permissions.core import GraphPermissionChecker


class ChemtrailsPermissionBackend(ModelBackend):
    # supports_object_permissions = True
    # supports_anonymous_user = True
    # supports_inactive_user = True

    def authenticate(self, username=None, password=None, **kwargs):
        return False

    def has_perm(self, user_obj, perm, obj=None):
        if '.' in perm:
            app_label, _ = perm.split('.', 1)
            ctype = ContentType.objects.get_for_model(obj)
            if app_label != ctype.app_label:
                raise Exception('Mismatch - TODO: Write a proper message here!')

        checker = GraphPermissionChecker(user_obj)
        return checker.has_perm(perm, obj)

    def get_all_permissions(self, user_obj, obj=None):
        checker = GraphPermissionChecker(user_obj)
        return checker.get_perms(obj)
