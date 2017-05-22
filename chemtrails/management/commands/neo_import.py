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
                cntr =0
                for model in apps.get_app_config(app_label=app).get_models():
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
                skip_count = 0
                for row in spamreader:

                    if row[0] == 'n':
                        # print(row[1])
                        try:
                            db.cypher_query(row[1])
                        except exception.UniqueProperty:
                             skip_count+=1

                if skip_count > 0:
                    self.stdout.write(self.style.SUCCESS(
                        '{} Nodes already existed, and was not updated'.format(skip_count)))

                self.stdout.write(self.style.SUCCESS('Crucifixion party! By the left! Forward!'))

            with open(target_file.name, newline='') as csvfile:
                spamreader = csv.reader(csvfile, delimiter=';', quotechar='|')
                self.stdout.write(self.style.SUCCESS('Crucifixion party! Wait for it...'))
                for row in spamreader:
                    if row[0] == 'r':
                        # print(row[1])
                        db.cypher_query(row[1])
                self.stdout.write(self.style.SUCCESS('Crucifixion party! By the left! Forward!'))

            self.stdout.write(self.style.SUCCESS('Successfully imported spam'))
        finally:
            target_file.close()

