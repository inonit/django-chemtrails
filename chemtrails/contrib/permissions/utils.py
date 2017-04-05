# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType


def get_identity(identity):
    """
    Returns (user_obj, None) or (None, group_obj) tuple depending on
    given ``identity`` argument.
    @:param  identity: ``User`` or ``Group`` object instance. 
    """
    if isinstance(identity, AnonymousUser):
        pass

    if isinstance(identity, get_user_model()):
        return identity, None
    elif isinstance(identity, Group):
        return None, identity


def get_content_type(obj):
    return ContentType.objects.get_for_model(obj)
