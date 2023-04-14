import csv

import django.db.utils
from django.core.management.base import BaseCommand

from bsf.models import LegoSet


class Command(BaseCommand):
    help = "Imports LegoSet models from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                try:
                    _, created = LegoSet.objects.get_or_create(
                        number=row[0],
                        name=row[1],
                        image_link=row[2],
                        inventory_id=row[3],
                    )
                    self.stdout.write(f'{row[3]} --> {row[0]}')
                except ValueError as e:
                    self.stdout.write(f'Something broke: {e}')
                except django.db.utils.IntegrityError as e:
                    self.stdout.write(f'Something really broke: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created LegoSets')
        )
