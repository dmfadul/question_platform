from django.core.management.base import BaseCommand
from django.db import transaction

from intake.management.csv_utils import (
    CSV_FILES,
    generate_discipline_code,
    read_csv,
)
from intake.models import Discipline


class Command(BaseCommand):
    help = "Import disciplines from the three cohort CSV files."

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0
        skipped_count = 0

        processed_names = set()

        with transaction.atomic():

            for csv_path in CSV_FILES:
                self.stdout.write(
                    f"Reading {csv_path}..."
                )

                for row_number, row in enumerate(
                    read_csv(csv_path),
                    start=2,
                ):
                    discipline_name = row.get(
                        "DISCIPLINAS",
                        "",
                    ).strip()

                    if not discipline_name:
                        self.stderr.write(
                            f"{csv_path}:{row_number}: "
                            f"Discipline name is empty."
                        )

                        skipped_count += 1
                        continue

                    normalized_name = discipline_name.casefold()

                    # Same discipline appearing in another
                    # cohort should only be processed once.
                    if normalized_name in processed_names:
                        continue

                    processed_names.add(normalized_name)

                    code = generate_discipline_code(
                        discipline_name
                    )

                    discipline = Discipline.objects.filter(
                        name__iexact=discipline_name,
                    ).first()

                    if discipline:
                        existing_count += 1
                        continue

                    Discipline.objects.create(
                        name=discipline_name,
                        code=code,
                        description="",
                    )

                    created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created: "
                            f"{discipline_name} "
                            f"[{code}]"
                        )
                    )

        self.stdout.write("")

        self.stdout.write(
            self.style.SUCCESS(
                "Discipline import finished."
            )
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Existing: {existing_count}"
        )

        self.stdout.write(
            f"Skipped: {skipped_count}"
        )