# -*- coding: utf-8 -*-


class Neo4jPermissionBackend(object):

    @staticmethod
    def authenticate(username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        pass