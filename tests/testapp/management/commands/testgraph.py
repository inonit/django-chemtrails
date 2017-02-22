# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand
from django.utils.translation import ungettext

from chemtrails.neoutils import get_nodeset_for_queryset

from tests.testapp.autofixtures import StoreFixture
from tests.testapp.models import Store


class Command(BaseCommand):
    help = 'Creates a bookstore test graph'

    def add_arguments(self, parser):
        parser.add_argument('count', type=int, help='Number of separate graph trees to create.')

        parser.add_argument(
            '--connection-depth', '-c',
            dest='depth',
            default=1,
            type=int,
            help='Maximum depth of recursive connections to be made.'
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('Hang tight, this might take a little while...'))
        count = options['count']
        depth = options['depth']
        queryset = Store.objects.filter(pk__in=map(lambda n: n.pk,
                                                   StoreFixture(Store).create(count=count, commit=True)))
        get_nodeset_for_queryset(queryset, sync=True, max_depth=depth)
        self.stdout.write(self.style.SUCCESS(ungettext(
            'Successfully created %(count)d bookstore graph.\nCheck it out in the Neo4j web console!',
            'Successfully created %(count)d bookstore graphs.\nCheck them out in the Neo4j web console!', count
        ) % {'count': count}))
