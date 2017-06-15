# -*- coding: utf-8 -*-

import os

from django.test import TestCase
from chemtrails import utils


class UtilsTestCase(TestCase):

    def setUp(self):
        os.environ['TRUE'] = 'TRUE'
        os.environ['True'] = 'True'
        os.environ['true'] = 'true'
        os.environ['FALSE'] = 'FALSE'
        os.environ['False'] = 'False'
        os.environ['false'] = 'false'
        os.environ['0'] = '0'
        os.environ['1'] = '1'
        os.environ['1.0'] = '1.0'

    def test_get_environment_variable_bool(self):
        self.assertTrue(utils.get_environment_variable('TRUE'))
        self.assertTrue(utils.get_environment_variable('True'))
        self.assertTrue(utils.get_environment_variable('true'))

        self.assertFalse(utils.get_environment_variable('FALSE'))
        self.assertFalse(utils.get_environment_variable('False'))
        self.assertFalse(utils.get_environment_variable('false'))

    def test_get_environment_variable_int(self):
        self.assertEqual(utils.get_environment_variable('0'), 0)
        self.assertEqual(utils.get_environment_variable('1'), 1)

    def test_get_environment_variable_float(self):
        self.assertEqual(utils.get_environment_variable('1.0'), 1.0)
