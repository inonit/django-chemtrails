from django.core.management.base import BaseCommand, CommandError
from chemtrails.neoutils import get_node_class_for_model
from django.apps import apps
from chemtrails import settings
import csv
import tempfile
from neomodel import db, exception


class Command(BaseCommand):
    help = 'imports current database to neo4j'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('test', type=int)

    def handle(self, *args, **options):

        target_file = tempfile.NamedTemporaryFile(delete=True)

        try:
            for app in apps.all_models:
                self.stdout.write(self.style.SUCCESS('Looking at {}'.format(app)))
                cntr =0
                model_count =0

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
                cypher = ''
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                self.stdout.write(self.style.SUCCESS('Crucifixion party! Wait for it...'))
                node_count = 0
                skip_count = 0
                for n, row in enumerate(spamreader):

                    if row[0] == 'n':
                        # print(row[1])
                        try:
                            cypher += row[1]
                            node_count += 1
                        except exception.UniqueProperty:
                             skip_count+=1
                db.cypher_query(cypher)
                self.stdout.write(self.style.SUCCESS(
                    '{} Nodes processed and delivered to Neo... '
                    'Why oh why, didn\'t I take the blue pill??'.format(node_count)))
                if skip_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        '{} Nodes already existed, and was not updated.... Were you listening to me Neo? Or were you '
                        'looking at the woman in the red dress?'.format(skip_count)))

            with open(target_file.name, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                node_count = 0
                for row in spamreader:
                    if row[0] == 'r':
                        # print(row[1])
                        db.cypher_query(row[1])
                        node_count += 1

                self.stdout.write(self.style.SUCCESS(
                    '{} Relations processed and delivered to Neo... '
                    'Why oh why, didn\'t I take the blue pill??'.format(node_count)))
                self.stdout.write(self.style.SUCCESS('Crucifixion party! By the left! Forward!'))


        finally:
            target_file.close()

