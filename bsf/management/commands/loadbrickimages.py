import csv

from django.core.management.base import BaseCommand

from bsf.models import Brick


class Command(BaseCommand):
    help = "Imports Brick images from CSV file"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                try:
                    bricks = Brick.objects.filter(part_num=row[1])
                    for brick in bricks:
                        brick.image_link = row[5]
                        self.stdout.write(f'{brick.brick_id} <- {brick.image_link}')
                        brick.save()

                except ValueError as e:
                    self.stdout.write(f'Something broke: {e}')

        self.stdout.write(
            self.style.SUCCESS('Successfully created Bricks')
        )
