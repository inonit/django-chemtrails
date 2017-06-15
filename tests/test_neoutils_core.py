# -*- coding: utf-8 -*-

from django.contrib.auth.models import Group, Permission, User
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.db.models.signals import post_save, m2m_changed
from django.test import TestCase, override_settings
from django.utils import six

from neomodel import *
from neomodel.match import NodeSet

from chemtrails import settings
from chemtrails.neoutils import (
    ModelNodeMeta, ModelNodeMixin, MetaNodeMeta, MetaNodeMixin,
    get_meta_node_class_for_model, get_meta_node_for_model,
    get_node_class_for_model, get_node_for_object, get_nodeset_for_queryset
)
from chemtrails.signals.handlers import post_save_handler, m2m_changed_handler
from chemtrails.utils import flatten

from tests.utils import flush_nodes
from tests.testapp.autofixtures import (
    Author,
    Book, BookFixture, Publisher, PublisherFixture, Store, StoreFixture, Tag
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
    def test_create_node_class_adds_to_cache(self):

        klass1 = get_node_class_for_model(Book)

        @six.add_metaclass(ModelNodeMeta)
        class ModelNode(ModelNodeMixin, StructuredNode):
            class Meta:
                model = Book

        klass2 = get_node_class_for_model(Book)
        self.assertEqual(klass1, klass2)

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

    @flush_nodes()
    def test_save_existing_node_is_updated(self):
        group = Group.objects.create(name='a group')

        node1 = get_node_for_object(group)
        self.assertEqual(group.name, node1.name)

        group.name = 'still the same group'
        group.save()

        node2 = get_node_for_object(group)
        self.assertEqual(group.name, node2.name)

        self.assertEqual(node1.id, node2.id)

    @flush_nodes()
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
        # self.assertEqual(klass.get_property_class_for_field(ArrayField), ArrayProperty)
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
    def test_update_raw_node_property(self):
        group = Group.objects.create(name='group')
        node = get_node_for_object(group)

        # Set a custom attribute on the node and make sure it's saved on the node
        result, _ = list(flatten(db.cypher_query('MATCH (n) WHERE ID(n) = %d '
                                                 'SET n.foo = "bar", n.baz = "qux" RETURN n' % node.id)))
        self.assertTrue(all(i in result.properties for i in ('foo', 'baz')))
        self.assertEqual(result.properties['foo'], 'bar')
        self.assertEqual(result.properties['baz'], 'qux')

        self.assertFalse(all(hasattr(node, i) for i in ('foo', 'baz')))
        node.__update_raw_node__()

        # Make sure the custom attribute has been deleted
        result, _ = list(flatten(db.cypher_query('MATCH (n) WHERE ID(n) = %d RETURN n' % node.id)))
        self.assertFalse(all(i in result.properties for i in ('foo', 'baz')))

    @flush_nodes()
    def test_update_raw_node_relationship(self):
        group1, group2 = Group.objects.create(name='group1'), Group.objects.create(name='group2')
        node1, node2 = get_node_for_object(group1), get_node_for_object(group2)

        # Create a custom relationship between group1 and group2
        results, _ = db.cypher_query(
            'MATCH (a), (b) WHERE ID(a) = %d AND ID(b) = %d '
            'CREATE (a)-[r1:RELATION]->(b), (b)-[r2:RELATION]->(a) '
            'RETURN r1, r2' % (node1.id, node2.id)
        )
        results = list(flatten(results))
        self.assertEqual(len(results), 2)
        self.assertTrue(all([r.type == 'RELATION' for r in results]))

        node1.__update_raw_node__()

        # Make sure custom relationship is deleted
        results, _ = db.cypher_query('MATCH (n)-[r]->() WHERE ID(n) = %d RETURN r' % node1.id)
        self.assertEqual(len(results), 0)

        # The other relationship should still be intact
        results, _ = db.cypher_query('MATCH (n)-[r]->() WHERE ID(n) = %d RETURN r' % node2.id)
        results = list(flatten(results))
        self.assertEqual(len(results), 1)

    def test_ignored_models_app_label(self):
        default = settings.IGNORE_MODELS
        try:
            settings.IGNORE_MODELS = ['auth']

            klass = get_node_class_for_model(Group)
            self.assertTrue(klass._is_ignored)

            klass = get_node_class_for_model(Book)
            self.assertFalse(klass._is_ignored)
        finally:
            settings.IGNORE_MODELS = default

    def test_ignored_models_app_label_wildcard(self):
        default = settings.IGNORE_MODELS
        try:
            settings.IGNORE_MODELS = ['auth.*']

            klass = get_node_class_for_model(Group)
            self.assertTrue(klass._is_ignored)

            klass = get_node_class_for_model(Book)
            self.assertFalse(klass._is_ignored)
        finally:
            settings.IGNORE_MODELS = default

    def test_ignored_models_app_label_model_name(self):
        default = settings.IGNORE_MODELS
        try:
            settings.IGNORE_MODELS = ['auth.group']

            klass = get_node_class_for_model(Group)
            self.assertTrue(klass._is_ignored)

            klass = get_node_class_for_model(Permission)
            self.assertFalse(klass._is_ignored)
        finally:
            settings.IGNORE_MODELS = default

    def test_ignore_model_save(self):
        # Make sure ignored models are not saved
        pass

    def test_ignored_model_sync(self):
        # Make sure ignored models are not synced
        pass

    def test_related_ignore_model_sync(self):
        # Make sure an ignored related model is not synced
        pass

    @flush_nodes()
    def test_recursive_connect(self):
        post_save.disconnect(post_save_handler, dispatch_uid='chemtrails.signals.handlers.post_save_handler')
        m2m_changed.disconnect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
        try:
            book = BookFixture(Book, generate_m2m={'authors': (1, 1)}).create_one()
            for depth in range(3):
                db.cypher_query('MATCH (n)-[r]-() WHERE n.type = "ModelNode" DELETE r')  # Delete all relationships
                book_node = get_node_for_object(book).save()
                book_node.recursive_connect(depth)

                if depth == 0:
                    # Max depth 0 means that no recursion should occur, and no connections
                    # can be made, because the connected objects might not exist.
                    for prop in book_node.defined_properties(aliases=False, properties=False).keys():
                        relation = getattr(book_node, prop)
                        self.assertEqual(len(relation.all()), 0)
                elif depth == 1:
                    self.assertEqual(0, len(get_node_class_for_model(Book).nodes.has(store_set=True)))
                    self.assertEqual(0, len(get_node_class_for_model(Store).nodes.has(books=True)))

                    self.assertEqual(0, len(get_node_class_for_model(Book).nodes.has(bestseller_stores=True)))
                    self.assertEqual(0, len(get_node_class_for_model(Store).nodes.has(bestseller=True)))

                    self.assertEqual(1, len(get_node_class_for_model(Book).nodes.has(publisher=True)))
                    self.assertEqual(1, len(get_node_class_for_model(Publisher).nodes.has(book_set=True)))

                    self.assertEqual(1, len(get_node_class_for_model(Book).nodes.has(authors=True)))
                    self.assertEqual(1, len(get_node_class_for_model(Author).nodes.has(book_set=True)))

                    self.assertEqual(0, len(get_node_class_for_model(Author).nodes.has(user=True)))
                    self.assertEqual(0, len(get_node_class_for_model(User).nodes.has(author=True)))

                    self.assertEqual(1, len(get_node_class_for_model(Book).nodes.has(tags=True)))
                    self.assertEqual(0, len(get_node_class_for_model(Tag).nodes.has(content_type=True)))

                elif depth == 2:
                    self.assertEqual(1, len(get_node_class_for_model(Author).nodes.has(user=True)))
                    self.assertEqual(1, len(get_node_class_for_model(User).nodes.has(author=True)))
                    self.assertEqual(1, len(get_node_class_for_model(Tag).nodes.has(content_type=True)))
                    self.assertEqual(1, len(get_node_class_for_model(ContentType)
                                            .nodes.has(content_type_set_for_tag=True)))
        finally:
            post_save.connect(post_save_handler, dispatch_uid='chemtrails.signals.handlers.post_save_handler')
            m2m_changed.connect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
