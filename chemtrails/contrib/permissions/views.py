# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.serializers import AccessRuleSerializer


class AccessRuleViewSet(ModelViewSet):

    queryset = AccessRule.objects.all()
    serializer_class = AccessRuleSerializer
