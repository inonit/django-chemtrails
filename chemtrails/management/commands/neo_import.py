from django.core.management.base import BaseCommand, CommandError
from chemtrails.neoutils import get_node_class_for_model
from django.apps import apps
from chemtrails.conf import settings
import csv
import tempfile
from neomodel import db, exception


class Command(BaseCommand):
    help = 'imports current database to neo4j'

    def add_arguments(self, parser):
        pass

    def handle(self, *args, **options):

        target_file = tempfile.NamedTemporaryFile(delete=True)
        BUFFER_COUNT = 100

        try:
            for app in apps.all_models:
                self.stdout.write(self.style.SUCCESS('Looking at {}'.format(app)))
                model_count = 0
                cntr = 0

                for n, model in enumerate(apps.get_app_config(app_label=app).get_models()):
                    model_count += 1
                    cls = get_node_class_for_model(model)
                    if cls._is_ignored:
                        continue

                    for item in model.objects.all():
                        node = cls(instance=item, bind=False)
                        node.to_csv(cntr=cntr, target_file=target_file)
                        cntr += 1

            with open(target_file.name, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                self.stdout.write(self.style.SUCCESS('Crucifixion party! Wait for it...'))
                node_count = 0
                skip_count = 0
                cypher = ''

                for row in spamreader:
                    if row[0] == 'n':
                        try:
                            cypher += row[1]
                            node_count += 1
                        except exception.UniqueProperty:
                            skip_count += 1

                    if cypher and node_count % BUFFER_COUNT == 0:
                        db.cypher_query(cypher)
                        cypher = ''
                        self.stdout.write('{} nodes processed'.format(node_count), ending='\r')
                        self.stdout.flush()

                if cypher:
                    db.cypher_query(cypher)

                self.stdout.write(self.style.SUCCESS(
                    '{} nodes processed and delivered to Neo... '
                    'Why oh why, didn\'t I take the blue pill??'.format(node_count)))
                if skip_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        '{} nodes already existed, and was not updated.... Were you listening to me Neo? Or were you '
                        'looking at the woman in the red dress?'.format(skip_count)))

            with open(target_file.name, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                relation_count = 0

                for row in spamreader:
                    if row[0] == 'r':
                        db.cypher_query(row[1])
                        relation_count += 1

                    if relation_count % BUFFER_COUNT == 0:
                        self.stdout.write('{} relations processed'.format(relation_count), ending='\r')
                        self.stdout.flush()

                self.stdout.write(self.style.SUCCESS(
                    '{} relations processed and delivered to Neo... '
                    'Why oh why, didn\'t I take the blue pill??'.format(relation_count)))
                self.stdout.write(self.style.SUCCESS('Crucifixion party! By the left! Forward!'))

        finally:
            target_file.close()

