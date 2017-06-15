# -*- coding: utf-8 -*-

from itertools import chain

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser, Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.shortcuts import _get_queryset
from django.utils.encoding import force_text

from neo4j.v1 import Node
from neomodel import db
from rest_framework.compat import is_anonymous

from chemtrails.contrib.permissions.exceptions import MixedContentTypeError
from chemtrails.neoutils import get_node_class_for_model, InflateError
from chemtrails.neoutils.query import validate_cypher
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.utils import flatten

User = get_user_model()


def get_identity(identity):
    """
    Returns (user_obj, None) or (None, group_obj) tuple depending on
    given ``identity`` argument.
    @:param  identity: ``User`` or ``Group`` object instance. 
    """
    if isinstance(identity, AnonymousUser):
        raise NotImplementedError('Implement support for AnonymousUser, please!')

    if isinstance(identity, User):
        return identity, None
    elif isinstance(identity, Group):
        return None, identity


def get_content_type(obj):
    """
    Returns the content type for ``obj``.
    """
    return ContentType.objects.get_for_model(obj)


def get_perms(user_or_group, model):
    """
    Return permissions for given user/group and model pair, as
    a list of strings.
    """
    checker = GraphPermissionChecker(user_or_group)
    return checker.get_perms(model)


def get_user_perms(user, model):
    """
    Return permissions for given user and model pair, as a 
    list of strings.
    """
    checker = GraphPermissionChecker(user)
    return checker.get_user_perms(model)


def check_permissions_app_label(permissions):
    """
    Make sure ``permissions`` matches the ``klass`` app label.
    
    :param permissions: Single permission string or a sequence of permission strings.
      Must be in the format "app_label.codename".
    :type permissions: str or sequence.
    
    :raises MixedContentTypeError: If given a sequence of ``permissions`` with different
      app labels.
    :raises MixedContentTypeError: If computed content type for ``permissions``
      and/or ``klass`` clashes.
    :raises ContentType.DoesNotExist: If failed to look up content type for permission.
    
    :returns: Two tuple with ContentType for permissions and a set of permission codenames.
    :rtype: tuple(ContentType, set(str,))
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
                raise MixedContentTypeError('Given permissions must have the same app label '
                                            '(%s != %s).' % (app_label, _app_label))
            app_label = _app_label
        else:
            codename = perm

        codenames.add(codename)
        if app_label is not None:
            _ctype = ContentType.objects.get(app_label=app_label,
                                             permission__codename=codename)
            if ctype is not None and ctype != _ctype:
                raise MixedContentTypeError('Calculated content type from permission "%s" %s does '
                                            'not match %r.' % (perm, _ctype, ctype))
            else:
                ctype = _ctype

    return ctype, codenames


def get_users_with_perms(obj, attach_perms=False, with_superusers=False, with_group_users=True):
    """
    Returns a queryset of all ``User`` objects which there can be calculated a path from
    the given ``obj``.
    """
    raise NotImplementedError


def get_groups_with_perms(obj, attach_perms=False):
    """
    Returns a queryset of ``Group`` objects which there can be calculated a path from
    the given ``obj``.
    """
    raise NotImplementedError


def get_objects_for_user(user, permissions, klass=None, use_groups=True,
                         extra_perms=None, any_perm=False, with_superuser=True):
    """
    Returns a queryset of objects for which there can be calculated a path between
    the ``user`` using one or more access rules with *all* permissions present
    at ``permissions``.
    
    :param user: ``User`` instance for which objects should be returned.
    :param permissions: Single permission string, or sequence of permission
      strings that should be checked.
      If ``klass`` parameter is not given, those should be full permission
      strings rather than only codenames (ie. ``auth.change_user``). If more than
      one permission is present in the sequence, their content type **must** be 
      the same or ``MixedContentTypeError`` would be raised.
    :param klass: May be a ``Model``, ``Manager`` or ``QuerySet`` object. If not
      given, this will be calculated based on passed ``permissions`` strings.
    :param use_groups: If ``True``, include users groups permissions.
      Defaults to ``True``.
    :param extra_perms: Single permission string, or sequence of permission strings
      that should be used as ``global_perms`` base. These permissions will be 
      treated as if the user possesses them.
    :param any_perm: If ``True``, any permission in sequence is accepted. 
      Defaults to ``False``.
    :param with_superuser: If ``True`` and ``user.is_superuser`` is set, returns
      the entire queryset. Otherwise will only return the objects the user has 
      explicit permissions to. Defaults to ``True``.
     
    :raises MixedContentTypeError: If computed content type for ``permissions``
      and/or ``klass`` clashes.
    :raises ValueError: If unable to compute content type for ``permissions``.
    
    :returns: QuerySet containing objects ``user`` has ``permissions`` to.
    """
    # Make sure all permissions checks out!
    ctype, codenames = check_permissions_app_label(permissions)
    if extra_perms:
        extra_ctype, extra_perms = check_permissions_app_label(extra_perms)
        if extra_ctype != ctype:
            raise MixedContentTypeError('Calculated content type from keyword argument `extra_perms` '
                                        '%s does not match %r.' % (extra_ctype, ctype))
    extra_perms = extra_perms or set()

    if ctype is None and klass is not None:
        queryset = _get_queryset(klass)
        ctype = get_content_type(queryset.model)
    elif ctype is not None and klass is None:
        queryset = _get_queryset(ctype.model_class())
    elif klass is None:
        raise ValueError('Could not determine the content type.')
    else:
        queryset = _get_queryset(klass)
        if ctype.model_class() != queryset.model:
            raise MixedContentTypeError('ContentType for given permissions and klass differs.')

    # Superusers have access to all objects.
    if with_superuser and user.is_superuser:
        return queryset

    # We don't support anonymous users.
    if is_anonymous(user):
        return queryset.none()

    # If there is no node in the graph for the user object, return empty queryset.
    source_node = get_node_class_for_model(user).nodes.get_or_none(**{'pk': user.pk})
    if not source_node:
        return queryset.none()

    # Next, get all permissions the user has, either directly set through user permissions
    # or if ``use_groups`` are set, derived from a group membership.
    global_perms = extra_perms | set(get_perms(user, queryset.model) if use_groups
                                     else get_user_perms(user, queryset.model))

    # Check if we requires the user to have *all* permissions or if it is
    # sufficient with any provided.
    if not any_perm and not all((code in global_perms for code in codenames)):
        return queryset.none()
    elif any_perm:
        for code in codenames.copy():
            if code not in global_perms:
                codenames.remove(code)

    # Retrieve all defined access rules originating from user content types,
    # and targets `queryset.model`.
    # To reduce search space, first retrieve all access rules with n or greater permissions count.
    rules_queryset = (AccessRule.objects.prefetch_related('permissions')
                      .annotate(count=Count('permissions')).filter(count__gte=len(codenames)))
    rules_queryset = rules_queryset.filter(ctype_source=get_content_type(user),
                                           ctype_target=ctype, is_active=True,
                                           permissions__codename__in=codenames)

    # Calculate a PATH query for each rule
    queries = []
    for access_rule in rules_queryset:
        manager = source_node.paths
        for n, rule_definition in enumerate(access_rule.relation_types_obj):
            relation_type, target_props = zip(*rule_definition.items())
            relation_type, target_props = relation_type[0], target_props[0]  # TODO: This should be validated before save!

            source_props = {}
            if n == 0 and access_rule.requires_staff:
                source_props.update({'is_staff': True})
            manager = manager.add(relation_type, source_props=source_props, target_props=target_props)

        if manager.statement:
            queries.append(manager.get_match())

    q_values = Q()
    klass = get_node_class_for_model(queryset.model)
    for query in queries:
        # FIXME: https://github.com/inonit/libcypher-parser-python/issues/1
        # validate_cypher(query, raise_exception=True)
        result, _ = db.cypher_query(query)
        if result:
            values = set()
            for item in flatten(result):
                if not isinstance(item, Node):
                    continue  # pragma: no cover
                try:
                    if klass.__label__ in item.labels:
                        node = get_node_class_for_model(queryset.model).inflate(item)
                        values.add(node.pk)
                except InflateError:  # pragma: no cover
                    continue
            q_values |= Q(pk__in=values)

    # If no values in the Q filter, it means we couldn't get a path from the
    # user node to given object in queryset by any evaluated rule.
    # Return an empty queryset.
    if not q_values:
        return queryset.none()
    return queryset.filter(q_values)


def get_objects_for_group(group, perms, klass=None, any_perm=False, accept_global_perms=True):
    """
    Returns a queryset of objects for which there can be calculated a path....
    """
    raise NotImplementedError


class GraphPermissionChecker(object):
    """
    Object permission checker inspired by django-guardian.
    """
    def __init__(self, user_or_group=None):
        self._obj_perms_cache = {}
        self.user, self.group = get_identity(user_or_group)

    def has_perm(self, perm, obj):
        """
        Checks if a user/group has given permission for object.
        """
        if self.user and not self.user.is_active:
            return False
        elif self.user and self.user.is_superuser:
            return True

        # We only care about the codename.
        perm = perm.split('.')[-1]
        has_perm = perm in self.get_perms(obj) and self.is_authorized(perm, obj)
        return has_perm

    def is_authorized(self, perm, obj):
        """
        Checks if user/group is authorized to access given object.
        """
        target_node = get_node_class_for_model(obj).nodes.get_or_none(**{'pk': obj.pk})
        if not target_node:
            return False

        if self.user:
            queryset = get_objects_for_user(self.user, perm, klass=obj._meta.default_manager.filter(pk=obj.pk))
            return obj in queryset
        elif self.group:
            # TODO: Implement `get_objects_for_group`!
            queryset = get_objects_for_group(self.group, perm, klass=obj._meta.default_manager.filter(pk=obj.pk))
            return obj in queryset

    @staticmethod
    def get_local_cache_key(obj):
        """
        Returns cache key for ``_obj_perms_cache`` dict.
        """
        ctype = get_content_type(obj)
        return ctype.id, force_text(obj.pk)

    @staticmethod
    def get_accessrule_queryset(obj):
        ctype = get_content_type(obj)
        return AccessRule.objects.filter(is_active=True, ctype_target=ctype)

    def get_user_filters(self):
        related_name = User.user_permissions.field.related_query_name()
        user_filters = {'%s' % related_name: self.user}
        return user_filters

    def get_user_perms(self, model):
        ctype = get_content_type(model)
        filters = self.get_user_filters()
        return Permission.objects.filter(content_type=ctype, **filters).values_list('codename', flat=True)

    def get_group_filters(self):
        related_name = Group.permissions.field.related_query_name()
        if self.user:
            field_name = '%s__%s' % (
                related_name,
                User.groups.field.related_query_name()
            )
            group_filters = {field_name: self.user}
        else:
            group_filters = {'%s' % related_name: self.group}

        return group_filters

    def get_group_perms(self, model):
        ctype = get_content_type(model)
        filters = self.get_group_filters()
        return Permission.objects.filter(content_type=ctype, **filters).values_list('codename', flat=True)

    def get_perms(self, obj):
        """
        Returns a list of permissions for given ``obj``.
        """
        if self.user and not self.user.is_active:
            return []

        ctype = get_content_type(obj)
        cache_key = self.get_local_cache_key(obj)
        if cache_key not in self._obj_perms_cache:
            if self.user and self.user.is_superuser:
                perms = list(chain(*Permission.objects
                                   .filter(content_type=ctype)
                                   .values_list('codename')))
            elif self.user:
                user_perms = self.get_user_perms(obj)
                group_perms = self.get_group_perms(obj)
                perms = list(set(chain(user_perms, group_perms)))
            else:
                group_filters = self.get_group_filters()
                perms = list(set(chain(*Permission.objects
                                       .filter(content_type=ctype, **group_filters)
                                       .values_list('codename'))))
            self._obj_perms_cache[cache_key] = perms
        return self._obj_perms_cache[cache_key]
