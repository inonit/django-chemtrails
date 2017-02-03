# -*- coding: utf-8 -*-

from datetime import datetime

import pytz
from django.test import TestCase

from neomodel import *

from tests.testapp.models import Book
from tests.testapp.autofixtures import BookFixture


class FriendRel(StructuredRel):
    since = DateTimeProperty(default=lambda: datetime.now(pytz.utc))
    met = StringProperty()


class Person(StructuredNode):
    name = StringProperty()
    friends = RelationshipTo('Person', 'FRIEND', model=FriendRel)


class SignalHandlerTestCase(TestCase):
    """
    Make sure that whenever a model is saved the changes are reflected
    in Neo4j.
    """

    def test_post_save_handler(self):
        BookFixture(Book).create(1)
        Book.objects.get()

    def test_create_node(self):

        person1 = Person(name='Fred').save()
        person2 = Person(name='Jimbo').save()

        person1.friends.connect(person2)

        self.assertIsInstance(person1, Person)



