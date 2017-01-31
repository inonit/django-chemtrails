# -*- coding: utf-8 -*-

from django.test import TestCase

from tests.testapp.models import Book
from tests.testapp.autofixtures import BookFixture


class SignalHandlerTestCase(TestCase):
    """
    Make sure that whenever a model is saved the changes are reflected
    in Neo4j.
    """

    def test_post_save_handler(self):
        BookFixture(Book).create(1)
