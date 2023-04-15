import csv

from django.core.management.base import BaseCommand

from bsf.models import LegoSet, Brick


class Command(BaseCommand):
    help = "Imports LegoSet models from inventory_parts.csv (step 2/3)"

    def add_arguments(self, parser):
        parser.add_argument("csv_path", nargs="+")

    def handle(self, *args, **options):
        with open(options["csv_path"][0]) as f:
            reader = csv.reader(f)
            next(reader, None)  # skip csv header
            for row in reader:
                try:
                    lego_sets = LegoSet.objects.filter(inventory_id=row[0])
                    brick = Brick.objects.filter(part_num=row[1]).first()
                    for lego_set in lego_sets:
                        lego_set.bricks.add(
                            brick, through_defaults={"quantity": row[3]}
                        )
                except Exception as e:
                    self.stdout.write(f"Something broke: {e}")

        self.stdout.write(self.style.SUCCESS("Successfully done step 2/3"))
