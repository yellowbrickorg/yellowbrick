import csv

from django.core.management.base import BaseCommand

from bsf.models import LegoSet, Brick


class Command(BaseCommand):
    help = "Imports LegoSet models from CSV file (step 2/3)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                try:
                    lego_set = LegoSet.objects.get(inventory_id=row[0])
                    brick = Brick.objects.get(number=row[1])
                    lego_set.bricks.add(brick, through_defaults={'quantity': row[3]})
                except ValueError:
                    self.stdout.write('Something broke but could not care less')

        self.stdout.write(
            self.style.SUCCESS('Successfully done step 2/3')
        )
