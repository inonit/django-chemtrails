# -*- coding: utf-8 -*-

import json
from django.core import serializers


class Neo4jDatasyncMixin(object):
    """
    Write Django model data to Neo4j database
    """

    def save(self, *args, **kwargs):
        super(Neo4jDatasyncMixin, self).save(*args, **kwargs)

        value = serializers.serialize('json', [self])
        value = json.loads(value[1:-1])  # Trim off square brackets!
        brk = ''
