from django.core.management.base import BaseCommand, CommandError
from chemtrails.neoutils import get_node_class_for_model
from django.apps import apps
from chemtrails import settings


class Command(BaseCommand):
    help = 'imports current database to neo4j'

    def add_arguments(self, parser):
        pass
        # parser.add_argument('test', type=int)

    def handle(self, *args, **options):

        for app in apps.all_models:
            if app not in settings.IGNORE_MODELS:
                self.stdout.write(self.style.SUCCESS(str(app)))

                filename = "eggs.csv"
                # opening the file with w+ mode truncates the file
                f = open(filename, "w+")
                f.close()
                for model in apps.get_app_config(app_label=app).get_models():
                    cls = get_node_class_for_model(model)
                    for item in model.objects.all():
                        node = cls(instance=item, bind=False)
                        node.to_csv()



        self.stdout.write(self.style.SUCCESS('Successfully imported spam'))
        pass
