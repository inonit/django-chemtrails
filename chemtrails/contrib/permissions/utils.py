# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group
from django.contrib.contenttypes.models import ContentType
from django.shortcuts import _get_queryset


def get_identity(identity):
    """
    Returns (user_obj, None) or (None, group_obj) tuple depending on
    given ``identity`` argument.
    @:param  identity: ``User`` or ``Group`` object instance. 
    """
    if isinstance(identity, AnonymousUser):
        raise NotImplementedError('Implement support for AnonymousUser, please!')

    if isinstance(identity, get_user_model()):
        return identity, None
    elif isinstance(identity, Group):
        return None, identity


def get_content_type(obj):
    """
    Returns the content type for ``obj``.
    """
    return ContentType.objects.get_for_model(obj)


def check_permissions_app_label(permissions):
    """
    Make sure ``permisssions`` matches the ``klass`` app label.
    :param permissions: Single permission string or a sequence of permission strings.
                        Must be in the format "app_label.codename".
    :type permissions: str or iterable.
    
    :raises: - ValueError if any of the compared permissions does not match.
             - ContentType.DoesNotExist if failed to look up content type for permission.
    :returns: Two tuple with ContentType for permissions and a list of permission codenames.
    :rtype: tuple(ContentType, list[str,])
    """
    if isinstance(permissions, str):
        permissions = [permissions]

    ctype = None
    app_label = None
    codenames = set()

    for perm in permissions:
        if '.' in perm:
            _app_label, codename = perm.split('.', 1)
            if app_label is not None and _app_label != app_label:
                raise ValueError('Given permisssions must have the same app label. '
                                 '(%s != %s)' % (app_label, _app_label))

            app_label = _app_label
        else:
            codename = perm

        codenames.add(codename)
        _ctype = ContentType.objects.get(app_label=app_label,
                                         permission__codename=codename)
        if ctype is not None and ctype != _ctype:
            raise ValueError('Calculated content type from permission "%s" %s does '
                             'not match %s.' % (perm, _ctype, ctype))
        else:
            ctype = _ctype

        if app_label != ctype.app_label:
            raise ValueError('Passed permission has app label "%s" while '
                             'given object has app label "%s". Make sure permission '
                             'matches the object.' %
                             (app_label, ctype.app_label))

    return ctype, list(codenames)


def get_objects_for_user(user, permissions, klass=None, use_groups=True, any_perm=False,
                         with_superuser=True, accept_global_perms=True):
    """
    Returns queryset of objects for which a given ``user`` has *all* permissions
    present at ``permissions``.
    This is inspired by ``django-guardian``.
    """
    # Make sure all permissions checks out!
    ctype, codenames = check_permissions_app_label(permissions)

    if ctype and klass is None:
        klass = ctype.model_class()
    elif klass is None:
        raise ValueError('Could not determine the content type.')

    queryset = _get_queryset(klass)

    if with_superuser and user.is_superuser:
        return queryset

    return klass



