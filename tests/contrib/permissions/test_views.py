# -*- coding: utf-8 -*-

import json

from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient

from chemtrails.contrib.permissions.models import AccessRule
from tests.utils import flush_nodes


class GraphWidgetAPIViews(APITestCase):

    def setUp(self):
        super(GraphWidgetAPIViews, self).setUp()
        self.client = APIClient(enforce_csrf_checks=True)

    def test_get_access_rule_list(self):
        response = self.client.get(reverse('admin:accessrule-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @flush_nodes()
    def test_get_access_rule_detail(self):
        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_by_natural_key('auth', 'user'),
            ctype_target=ContentType.objects.get_by_natural_key('testapp', 'book'),
            is_active=True,
            relation_types=[{'BOOK': None}]
        )
        access_rule.permissions.add(*list(Permission.objects.filter(codename__in=['add_book', 'change_book'])))
        response = self.client.get(reverse('admin:accessrule-detail', kwargs={'pk': access_rule.pk}))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    @flush_nodes()
    def test_post_access_rule(self):
        response = self.client.post(reverse('admin:accessrule-list'), data={
            'ctype_source': 'auth.user',
            'ctype_target': 'testapp.book',
            'permissions': [
                'testapp.add_book',
                'testapp.change_book',
                'testapp.delete_book'
            ],
            'relation_types': [{'BOOK': None}]
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @flush_nodes()
    def test_patch_access_rule(self):
        access_rule = AccessRule.objects.create(
            ctype_source=ContentType.objects.get_by_natural_key('auth', 'user'),
            ctype_target=ContentType.objects.get_by_natural_key('testapp', 'book'),
            is_active=True
        )
        response = self.client.patch(reverse('admin:accessrule-detail', kwargs={'pk': access_rule.pk}),
                                     data={'is_active': False}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        content = json.loads(response.content.decode())
        self.assertFalse(content['is_active'])
