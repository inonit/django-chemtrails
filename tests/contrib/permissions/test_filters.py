# -*- coding: utf-8 -*-

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

from rest_framework import status
from rest_framework.permissions import DjangoObjectPermissions
from rest_framework.serializers import ModelSerializer
from rest_framework.test import APIRequestFactory, force_authenticate
from rest_framework.viewsets import ModelViewSet

from chemtrails.contrib.permissions.models import AccessRule
from chemtrails.contrib.permissions.rest_framework.filters import ChemoPermissionsFilter
from chemtrails.contrib.permissions.utils import get_content_type

User = get_user_model()
factory = APIRequestFactory()


class ChemoPermissionsFilterTestCase(TestCase):

    def setUp(self):
        Group.objects.bulk_create([Group(name=name) for name in ['group1', 'group2', 'group3']])

        class GroupSerializer(ModelSerializer):
            class Meta:
                model = Group
                fields = '__all__'

        class GroupViewSet(ModelViewSet):
            queryset = Group.objects.all()
            serializer_class = GroupSerializer
            permission_classes = [DjangoObjectPermissions]
            filter_backends = [ChemoPermissionsFilter]

        self.user = User.objects.create_user(username='testuser', password='test123.')
        self.perm = Permission.objects.create(content_type=ContentType.objects.get_for_model(Group),
                                              name='Can view group', codename='view_group')
        self.access_rule = AccessRule.objects.create(ctype_source=get_content_type(User),
                                                     ctype_target=get_content_type(Group),
                                                     is_active=True,
                                                     relation_types=[
                                                         'GROUPS'
                                                     ])
        self.view = GroupViewSet

    def test_filter_get_list(self):
        groups = Group.objects.filter(name__in=['group1', 'group2'])
        self.user.user_permissions.add(self.perm)
        self.user.groups.add(*groups)
        self.access_rule.permissions.add(self.perm)

        request = factory.get(path='', content_type='application/json')
        force_authenticate(request, self.user)

        # User should now be able to see group1 and group2, but not group3
        response = self.view.as_view(actions={'get': 'list'})(request)
        self.assertEqual(len(response.data), len(groups))
        for result in response.data:
            self.assertTrue(result['name'] in groups.values_list('name', flat=True))

    def test_filter_get_detail(self):
        group1, group2 = (Group.objects.get(name='group1'),
                          Group.objects.get(name='group2'))
        self.user.user_permissions.add(self.perm)
        self.user.groups.add(group1)
        self.access_rule.permissions.add(self.perm)

        request = factory.get(path='', content_type='application/json')
        force_authenticate(request, self.user)

        response = self.view.as_view(actions={'get': 'retrieve'})(request, pk=group1.pk)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], group1.name)

        response = self.view.as_view(actions={'get': 'retrieve'})(request, pk=group2.pk)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.data, {'detail': 'Not found.'})

    def test_filter_post(self):
        pass

    def test_filter_put(self):
        pass

    def test_filter_patch(self):
        pass

    def test_filter_delete(self):
        pass

