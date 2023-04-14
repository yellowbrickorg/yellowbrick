import csv

from django.core.management.base import BaseCommand

from bsf.models import Brick


class Command(BaseCommand):
    help = "Imports Brick models from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                try:
                    _, created = Brick.objects.get_or_create(
                        brick_id=row[0],
                        part_num=row[1],
                        color_id=row[2],
                        image_link=row[3],
                    )
                except ValueError as e:
                    self.stdout.write(f'Something broke: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created Bricks')
        )
