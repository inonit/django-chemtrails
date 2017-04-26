# -*- coding: utf-8 -*-

from rest_framework.viewsets import ModelViewSet
from rest_framework.serializers import ModelSerializer
from rest_framework.permissions import DjangoObjectPermissions

from chemtrails.contrib.permissions.rest_framework.filters import ChemoPermissionsFilter

from tests.testapp.models import Book


class BookSerializer(ModelSerializer):
    class Meta:
        model = Book
        fields = '__all__'


class BookViewSet(ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer
    permission_classes = [DjangoObjectPermissions]
    filter_backends = [ChemoPermissionsFilter]

