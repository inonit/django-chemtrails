# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group, Permission
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase, override_settings
from django.utils import six

from neomodel import *
from neomodel.match import NodeSet

from chemtrails.neoutils import (
    ModelNodeMeta, ModelNodeMixin, MetaNodeMeta, MetaNodeMixin,
    get_meta_node_class_for_model, get_meta_node_for_model,
    get_node_class_for_model, get_node_for_object, get_nodeset_for_queryset
)

from tests.utils import flush_nodes
from tests.testapp.autofixtures import (
    Book, BookFixture, Publisher, PublisherFixture, Store, StoreFixture,
)


class NodeUtilsTestCase(TestCase):
    """
    Test various utility functions for dealing with
    model and node instances.
    """
    def test_get_meta_node_class_for_model(self):
        klass = get_meta_node_class_for_model(Book)
        self.assertTrue(issubclass(klass, StructuredNode))

    @flush_nodes()
    def test_get_meta_node_class_for_concrete_model(self):
        book = BookFixture(Book).create_one()
        klass = get_meta_node_class_for_model(book, for_concrete_model=True)
        self.assertTrue(issubclass(klass, StructuredNode))

    def test_get_node_class_for_model(self):
        klass = get_node_class_for_model(Book)
        self.assertTrue(issubclass(klass, StructuredNode))

    @flush_nodes()
    def test_get_node_class_for_model(self):
        book = BookFixture(Book).create_one()
        klass = get_node_class_for_model(book, for_concrete_model=True)
        self.assertTrue(issubclass(klass, StructuredNode))

    @flush_nodes()
    def test_get_meta_node_for_model(self):
        book_meta = get_meta_node_for_model(Book)
        self.assertIsInstance(book_meta, StructuredNode)

    @flush_nodes()
    def test_get_node_for_object(self):
        store = StoreFixture(Store).create_one(commit=True)
        store_node = get_node_for_object(store)
        self.assertIsInstance(store_node, get_node_class_for_model(Store))

    @flush_nodes()
    def test_get_nodeset_for_queryset(self):
        queryset = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                   StoreFixture(Store).create(count=2, commit=True)))
        nodeset = get_nodeset_for_queryset(queryset)
        self.assertIsInstance(nodeset, NodeSet)
        for node in nodeset:
            self.assertIsInstance(node, get_node_class_for_model(queryset.model))


class ModelNodeTestCase(TestCase):
    """
    Test that we can create ModelNode instances.
    """
    @flush_nodes()
    def test_create_model_node(self):
        book = BookFixture(Book).create_one()

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            class Meta:
                model = Book

        self.assertTrue(issubclass(ModelNode, StructuredNode))
        self.assertIsInstance(ModelNode(instance=book), StructuredNode)

    @flush_nodes()
    def test_create_model_with_content_types(self):
        permission = Permission.objects.latest('pk')

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            class Meta:
                model = Permission

        self.assertTrue(issubclass(ModelNode, StructuredNode))
        self.assertIsInstance(ModelNode(instance=permission), StructuredNode)

    def test_create_model_node_declaring_model_in_class(self):

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            __metaclass_model__ = Book

            class Meta:
                model = None

        self.assertEqual(ModelNode.Meta.model, Book)

    def test_create_model_node_custom_app_label(self):

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):

            class Meta:
                model = Book
                app_label = 'custom_app_label'

        self.assertEqual(ModelNode.Meta.app_label, 'custom_app_label')

    def test_create_model_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(ModelNodeMeta)
            class ModelNode(ModelNodeMixin, StructuredNode):

                class Meta:
                    model = None

            self.fail('Did not fail when defining a ModelNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'ModelNode')

    def test_create_model_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(ModelNodeMeta)
            class ModelNode(ModelNodeMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a ModelNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'ModelNode')

    def test_save_existing_node_is_updated(self):
        group = Group.objects.create(name='a group')

        node1 = get_node_for_object(group)
        self.assertEqual(group.name, node1.name)

        group.name = 'still the same group'
        group.save()

        node2 = get_node_for_object(group)
        self.assertEqual(group.name, node2.name)

        self.assertEqual(node1.id, node2.id)

    def test_sync_existing_node_is_updated(self):
        group = Group.objects.create(name='a group')

        node = get_node_for_object(group)
        self.assertEqual(group.name, node.name)

        group.name = 'another name'
        group.save()

        node.sync()
        self.assertEqual(group.name, node.name)


class MetaNodeTestCase(TestCase):
    """
    Test that we can create "singleton" meta nodes
    """
    def test_create_meta_node(self):

        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):

            class Meta:
                model = Book

        self.assertTrue(issubclass(MetaNode, StructuredNode))
        self.assertIsInstance(MetaNode(), StructuredNode)

    def test_create_meta_node_declaring_model_in_class(self):

        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            __metaclass_model__ = Book

            class Meta:
                model = None

        self.assertEqual(MetaNode.Meta.model, Book)

    def test_create_meta_node_custom_app_label(self):

        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):

            class Meta:
                model = Book
                app_label = 'custom_app_label'

        self.assertEqual(MetaNode.Meta.app_label, 'custom_app_label')

    def test_create_meta_node_custom_permissions(self):

        @six.add_metaclass(MetaNodeMeta)
        class MetaNode(MetaNodeMixin, StructuredNode):
            class Meta:
                model = Publisher

        self.assertEqual(MetaNode.Meta.model, Publisher)

    def test_create_meta_node_fails_without_meta_model(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class MetaNode(MetaNodeMixin, StructuredNode):

                class Meta:
                    model = None

            self.fail('Did not fail when defining a MetaNode with missing Meta class model.')
        except ValueError as e:
            self.assertEqual(str(e), '%s.Meta.model attribute cannot be None.' % 'MetaNode')

    def test_create_meta_node_fails_without_meta_class(self):
        try:
            @six.add_metaclass(MetaNodeMeta)
            class MetaNode(MetaNodeMixin, StructuredNode):
                pass

            self.fail('Did not fail when defining a MetaNode without a Meta class.')
        except ImproperlyConfigured as e:
            self.assertEqual(str(e), '%s must implement a Meta class.' % 'MetaNode')

    @flush_nodes()
    @override_settings(CHEMTRAILS={
        'CONNECT_META_NODES': True
    })
    def test_connected_meta_node(self):
        book = BookFixture(Book).create_one()
        meta = get_meta_node_for_model(Book).sync()

        # FIXME: Settings object is not updated when using override_settings


class GraphMapperTestCase(TestCase):
    """
    Test that node relationships are mapped correctly
    """

    def test_get_property_class_for_field(self):
        from django.contrib.contenttypes.fields import GenericRelation
        from django.contrib.postgres.fields import (
            ArrayField, HStoreField, JSONField,
            IntegerRangeField, BigIntegerRangeField, FloatRangeField,
            DateTimeRangeField, DateRangeField
        )
        from django.db import models

        class CustomField(object):
            pass

        klass = get_node_class_for_model(Book)

        self.assertEqual(klass.get_property_class_for_field(models.ForeignKey), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.ForeignKey), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.OneToOneField), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.ManyToManyField), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.ManyToOneRel), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.OneToOneRel), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(models.ManyToManyRel), RelationshipTo)
        self.assertEqual(klass.get_property_class_for_field(GenericRelation), RelationshipTo)

        self.assertEqual(klass.get_property_class_for_field(models.AutoField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.BigAutoField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.BooleanField), BooleanProperty)
        self.assertEqual(klass.get_property_class_for_field(models.CharField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.CommaSeparatedIntegerField), ArrayProperty)
        self.assertEqual(klass.get_property_class_for_field(models.DateField), DateProperty)
        self.assertEqual(klass.get_property_class_for_field(models.DateTimeField), DateTimeProperty)
        self.assertEqual(klass.get_property_class_for_field(models.DecimalField), FloatProperty)
        self.assertEqual(klass.get_property_class_for_field(models.DurationField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.EmailField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.FilePathField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.FileField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.FloatField), FloatProperty)
        self.assertEqual(klass.get_property_class_for_field(models.GenericIPAddressField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.IntegerField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.IPAddressField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.NullBooleanField), BooleanProperty)
        self.assertEqual(klass.get_property_class_for_field(models.PositiveIntegerField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.PositiveSmallIntegerField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.SlugField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.SmallIntegerField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.TextField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.TimeField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(models.URLField), StringProperty)
        self.assertEqual(klass.get_property_class_for_field(models.UUIDField), StringProperty)

        # Test special fields
        self.assertEqual(klass.get_property_class_for_field(ArrayField), ArrayProperty)
        self.assertEqual(klass.get_property_class_for_field(HStoreField), JSONProperty)
        self.assertEqual(klass.get_property_class_for_field(JSONField), JSONProperty)

        # Test undefined fields by inspecting their base classes.
        self.assertEqual(klass.get_property_class_for_field(models.BigIntegerField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(IntegerRangeField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(BigIntegerRangeField), IntegerProperty)
        self.assertEqual(klass.get_property_class_for_field(FloatRangeField), FloatProperty)
        self.assertEqual(klass.get_property_class_for_field(DateTimeRangeField), DateTimeProperty)
        self.assertEqual(klass.get_property_class_for_field(DateRangeField), DateProperty)

        # Test unsupported field
        self.assertRaisesMessage(
            NotImplementedError, 'Unsupported field. Field CustomField is currently not supported.',
            klass.get_property_class_for_field, CustomField)

    @flush_nodes()
    def test_sync_related_branch(self):
        queryset = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                   StoreFixture(Store).create(count=1, commit=True)))
        store_nodeset = get_nodeset_for_queryset(queryset, sync=True, max_depth=1)
        for store in store_nodeset:
            store_obj = store.get_object()

            if store_obj.bestseller:
                self.assertEqual(store.bestseller.get(), get_node_for_object(store_obj.bestseller))

            self.assertEqual(len(store.books.all()), store_obj.books.count())
            for book in store.books.all():
                book_obj = book.get_object()
                self.assertTrue(store in book.store_set.all())
                self.assertEqual(book.publisher.get(), get_node_for_object(book_obj.publisher))
                self.assertEqual(len(book.store_set.all()), book_obj.store_set.count())
                self.assertEqual(len(book.bestseller_stores.all()), book_obj.bestseller_stores.count())
                self.assertEqual(len(book.authors.all()), book_obj.authors.count())

                for author in book.authors.all():
                    author_obj = author.get_object()
                    self.assertTrue(book in author.book_set.all())

                    user = author.user.get()
                    self.assertEqual(user, get_node_for_object(author_obj.user).sync())
                    self.assertEqual(author, user.author.get())

