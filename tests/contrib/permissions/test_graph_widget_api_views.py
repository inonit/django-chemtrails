# -*- coding: utf-8 -*-

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase, APIClient


class GraphWidgetAPIViews(APITestCase):

    def setUp(self):
        super(GraphWidgetAPIViews, self).setUp()
        self.client = APIClient(enforce_csrf_checks=True)

    def test_get_access_rule_list(self):
        response = self.client.get(reverse('admin:accessrule-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
