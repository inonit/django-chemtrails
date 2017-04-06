# -*- coding: utf-8 -*-

from itertools import chain

from neo4j.v1 import Path

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission, Group
from django.utils.encoding import force_text

from neomodel import db, InflateError

from chemtrails.neoutils import get_node_class_for_model
from chemtrails.neoutils.query import validate_cypher
from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.utils import get_identity, get_content_type
from chemtrails.utils import flatten

User = get_user_model()


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
        source_node = (get_node_class_for_model(self.user or self.group)
                       .nodes.get_or_none(**{'pk': getattr(self.user, 'pk', None) or self.group.pk}))
        target_node = get_node_class_for_model(obj).nodes.get_or_none(**{'pk': obj.pk})

        if not source_node or not target_node:
            return False

        # For each rule assigned to the content type of the given object,
        # construct a `MATCH path = (...)` cypher query.
        queries = []
        for access_rule in self.get_accessrule_queryset(obj).filter(
                ctype_source=get_content_type(self.user or self.group),
                ctype_target=get_content_type(obj),
                permissions__codename=perm):

            statement = source_node.paths
            for n, relation_type in enumerate(access_rule.relation_types, 1):
                filters = {}
                if n == len(access_rule.relation_types):
                    filters.update({'pk': obj.pk})

                # Recalculate the `MATCH path = (...)` statement on each iteration.
                statement = statement.add(relation_type, **filters)

            if statement:
                queries.append(statement.get_path())

        # Execute all constructed path queries and return True on the first match.
        for query in queries:
            validate_cypher(query, raise_exception=True)
            result, _ = db.cypher_query(query)
            if result:
                for item in flatten(result):
                    if not isinstance(item, Path):
                        continue

                    # Inflate both the source node and target node and make sure
                    # they match.
                    try:
                        start_node = get_node_class_for_model(self.user or self.group).inflate(item.start)
                        end_node = get_node_class_for_model(obj).inflate(item.end)
                        if source_node == start_node and target_node == end_node:
                            return True
                    except InflateError:
                        continue

        return False

    def get_local_cache_key(self, obj):
        """
        Returns cache key for ``_obj_perms_cache`` dict.
        """
        ctype = get_content_type(obj)
        return ctype.id, force_text(obj.pk)

    def get_accessrule_queryset(self, obj):
        ctype = get_content_type(obj)
        return AccessRule.objects.filter(is_active=True, ctype_target=ctype)

    def get_user_filters(self):
        related_name = User.user_permissions.field.related_query_name()
        user_filters = {'%s' % related_name: self.user}
        return user_filters

    def get_user_perms(self, obj):
        ctype = get_content_type(obj)
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
            group_filters = {'%s__group' % related_name: self.group}

        return group_filters

    def get_group_perms(self, obj):
        ctype = get_content_type(obj)
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
