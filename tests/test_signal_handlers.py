# -*- coding: utf-8 -*-

from django.db.models.signals import post_save, pre_delete, m2m_changed
from django.test import TestCase

from chemtrails.neoutils import get_node_class_for_model
from chemtrails.signals.handlers import post_save_handler, pre_delete_handler, m2m_changed_handler

from tests.testapp.autofixtures import Author, Book, BookFixture
from tests.utils import flush_nodes


class PostSaveHandlerTestCase(TestCase):

    @flush_nodes()
    def test_create_new_object_is_synced(self):
        post_save.disconnect(post_save_handler, dispatch_uid='chemtrails.signals.handlers.post_save_handler')
        post_save.connect(post_save_handler, dispatch_uid='post_save_handler.test')
        try:
            book = BookFixture(Book).create_one()
            klass = get_node_class_for_model(Book)

            self.assertEqual(book.pk, klass.nodes.get(pk=book.pk).pk)
            self.assertEqual(1, len(klass.nodes.has(authors=True, publisher=True)))
        finally:
            post_save.connect(post_save_handler, dispatch_uid='chemtrails.signals.handlers.post_save_handler')
            post_save.disconnect(post_save_handler, dispatch_uid='post_save_handler.test')

    @flush_nodes()
    def test_delete_object_is_deleted(self):
        pre_delete.disconnect(pre_delete_handler, dispatch_uid='chemtrails.signals.handlers.pre_delete_handler')
        pre_delete.connect(pre_delete_handler, dispatch_uid='pre_delete_handler.test')
        try:
            book = BookFixture(Book).create_one()
            klass = get_node_class_for_model(Book)
            pk = book.pk
            try:
                book.delete()
                klass.nodes.get(pk=pk)
                self.fail('Did not raise when trying to get non-existent book node.')
            except klass.DoesNotExist as e:
                self.assertEqual(str(e), "{'pk': %d}" % pk)
        finally:
            pre_delete.connect(pre_delete_handler, dispatch_uid='chemtrails.signals.handlers.pre_delete_handler')
            pre_delete.disconnect(pre_delete_handler, dispatch_uid='pre_delete_handler.test')

    @flush_nodes()
    def test_m2m_changed_post_add_handler(self):
        m2m_changed.disconnect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
        m2m_changed.connect(m2m_changed_handler, dispatch_uid='m2m_changed_handler.test')
        try:
            pass
        finally:
            m2m_changed.connect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
            m2m_changed.disconnect(m2m_changed_handler, dispatch_uid='m2m_changed_handler.test')

    @flush_nodes()
    def test_m2m_changed_pre_clear(self):
        m2m_changed.disconnect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
        m2m_changed.connect(m2m_changed_handler, dispatch_uid='m2m_changed_handler.test')
        try:
            book = BookFixture(Book).create_one()
            self.assertTrue(len(get_node_class_for_model(Book).nodes.has(authors=True)) >= 1)

            book.authors.clear()
            self.assertEqual(0, len(get_node_class_for_model(Book).nodes.has(authors=True)))
            self.assertEqual(0, len(get_node_class_for_model(Author).nodes.has(book_set=True)))
        finally:
            m2m_changed.connect(m2m_changed_handler, dispatch_uid='chemtrails.signals.handlers.m2m_changed_handler')
            m2m_changed.disconnect(m2m_changed_handler, dispatch_uid='m2m_changed_handler.test')
