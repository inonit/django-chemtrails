# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer

from chemtrails.contrib.permissions.rest_framework.filters import ChemoPermissionsFilter
from chemtrails.contrib.permissions.rest_framework.permissions import ChemoPermissions

from tests.testapp.models import Book


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [ChemoPermissions]
    filter_backends = [ChemoPermissionsFilter]

