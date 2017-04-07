# -*- coding: utf-8 -*-

from rest_framework.permissions import DjangoObjectPermissions


class ChemoPermissions(DjangoObjectPermissions):
    """
    
    """
    def has_object_permission(self, request, view, obj):
        return super(ChemoPermissions, self).has_object_permission(request, view, obj)
