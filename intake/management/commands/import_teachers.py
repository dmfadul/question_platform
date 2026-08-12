from django.core.management.base import BaseCommand
from django.db import transaction

from intake.management.csv_utils import (
    CSV_FILES,
    generate_teacher_email,
    read_csv,
)
from intake.models import Teacher


class Command(BaseCommand):
    help = "Import teachers from the three cohort CSV files."

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
                    teacher_name = row.get(
                        "PROFESSORES",
                        "",
                    ).strip()

                    if not teacher_name:
                        self.stderr.write(
                            f"{csv_path}:{row_number}: "
                            f"Teacher name is empty."
                        )

                        skipped_count += 1
                        continue

                    normalized_name = teacher_name.casefold()

                    # Avoid processing the same person repeatedly
                    # across the three CSV files.
                    if normalized_name in processed_names:
                        continue

                    processed_names.add(normalized_name)

                    email = generate_teacher_email(
                        teacher_name
                    )

                    teacher, created = (
                        Teacher.objects.get_or_create(
                            name__iexact=teacher_name,
                            defaults={
                                "name": teacher_name,
                                "email": email,
                            },
                        )
                    )

                    if created:
                        created_count += 1

                        self.stdout.write(
                            self.style.SUCCESS(
                                f"Created: "
                                f"{teacher_name} "
                                f"<{email}>"
                            )
                        )

                    else:
                        existing_count += 1

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Teacher import finished."
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