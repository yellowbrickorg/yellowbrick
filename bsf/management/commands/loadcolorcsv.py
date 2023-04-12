import csv

from django.core.management.base import BaseCommand

from bsf.models import Color


class Command(BaseCommand):
    help = "Imports Color models from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                _, created = Color.objects.get_or_create(
                    color_id=row[0],
                    name=row[1],
                    rgb=row[2],
                    is_transparent=row[3],
                )

        self.stdout.write(
            self.style.SUCCESS('Successfully created Bricks')
        )
