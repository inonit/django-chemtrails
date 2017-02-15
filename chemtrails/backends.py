# -*- coding: utf-8 -*-


class ChemoPermissionBackend:
    """
    Object permission backend based on an autogenerated
    Neo4j graph of the database.
    """
    @staticmethod
    def authenticate(username, password):
        return None

    def has_perm(self, user_obj, perm, obj=None):
        pass
