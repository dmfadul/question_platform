from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from intake.management.csv_utils import (
    generate_teacher_email,
    generate_discipline_code,
    read_csv,
)
from intake.models import (
    Collection,
    Discipline,
    Invitation,
    Teacher,
)


class Command(BaseCommand):
    help = "Import invitations from a cohort CSV into an existing collection."

    def add_arguments(self, parser):
        parser.add_argument(
            "collection_id",
            type=int,
            help="ID of the collection that will receive the invitations.",
        )

        parser.add_argument(
            "csv_file",
            help="Path to the cohort CSV file.",
        )

    def handle(self, *args, **options):
        collection_id = options["collection_id"]
        csv_path = options["csv_file"]

        # --------------------------------------------------
        # Find collection
        # --------------------------------------------------

        try:
            collection = Collection.objects.get(
                pk=collection_id
            )

        except Collection.DoesNotExist as exc:
            raise CommandError(
                f"Collection with ID {collection_id} does not exist."
            ) from exc

        self.stdout.write(
            f"Collection: {collection}"
        )

        self.stdout.write(
            f"CSV: {csv_path}"
        )

        self.stdout.write("")

        created_count = 0
        updated_count = 0
        skipped_count = 0

        # Used to avoid processing an accidental duplicate
        # teacher + discipline row twice in the same CSV.
        processed = set()

        # --------------------------------------------------
        # Read CSV
        # --------------------------------------------------

        with transaction.atomic():

            for row_number, row in enumerate(
                read_csv(csv_path),
                start=2,
            ):
                # ------------------------------------------
                # Get values
                # ------------------------------------------

                teacher_name = row.get(
                    "PROFESSORES",
                    "",
                ).strip()

                discipline_name = row.get(
                    "DISCIPLINAS",
                    "",
                ).strip()

                solicitar = row.get(
                    "SOLICITAR",
                    "",
                ).strip()

                # QUANT and ID are intentionally ignored.

                # ------------------------------------------
                # Validate teacher
                # ------------------------------------------

                if not teacher_name:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {row_number}: "
                            f"PROFESSORES is empty. Skipping."
                        )
                    )

                    skipped_count += 1
                    continue

                # ------------------------------------------
                # Validate discipline
                # ------------------------------------------

                if not discipline_name:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {row_number}: "
                            f"DISCIPLINAS is empty. Skipping."
                        )
                    )

                    skipped_count += 1
                    continue

                # ------------------------------------------
                # Validate SOLICITAR
                # ------------------------------------------

                try:
                    expected_questions = int(solicitar)

                except (TypeError, ValueError):
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {row_number}: "
                            f"invalid SOLICITAR value "
                            f"{solicitar!r}. Skipping."
                        )
                    )

                    skipped_count += 1
                    continue

                if expected_questions < 0:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {row_number}: "
                            f"SOLICITAR cannot be negative. "
                            f"Skipping."
                        )
                    )

                    skipped_count += 1
                    continue

                # ------------------------------------------
                # Find teacher
                # ------------------------------------------

                teacher_email = generate_teacher_email(
                    teacher_name
                )

                try:
                    teacher = Teacher.objects.get(
                        email__iexact=teacher_email
                    )

                except Teacher.DoesNotExist:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Row {row_number}: "
                            f"Teacher not found: "
                            f"{teacher_name} "
                            f"<{teacher_email}>"
                        )
                    )

                    skipped_count += 1
                    continue

                # ------------------------------------------
                # Find discipline
                # ------------------------------------------

                discipline_code = generate_discipline_code(
                    discipline_name
                )

                try:
                    discipline = Discipline.objects.get(
                        code=discipline_code
                    )

                except Discipline.DoesNotExist:
                    self.stderr.write(
                        self.style.ERROR(
                            f"Row {row_number}: "
                            f"Discipline not found: "
                            f"{discipline_name} "
                            f"[{discipline_code}]"
                        )
                    )

                    skipped_count += 1
                    continue

                # ------------------------------------------
                # Avoid duplicate rows in the CSV
                # ------------------------------------------

                key = (
                    teacher.pk,
                    discipline.pk,
                )

                if key in processed:
                    self.stderr.write(
                        self.style.WARNING(
                            f"Row {row_number}: "
                            f"duplicate entry for "
                            f"{teacher.name} / "
                            f"{discipline.name}. Skipping."
                        )
                    )

                    skipped_count += 1
                    continue

                processed.add(key)

                # ------------------------------------------
                # Create/update invitation
                # ------------------------------------------

                invitation, created = (
                    Invitation.objects.update_or_create(
                        collection=collection,
                        teacher=teacher,
                        discipline=discipline,
                        defaults={
                            "expected_questions": expected_questions,
                            "is_active": True,
                        },
                    )
                )

                if created:
                    created_count += 1

                    self.stdout.write(
                        self.style.SUCCESS(
                            f"Created: "
                            f"{teacher.name} | "
                            f"{discipline.name} | "
                            f"{expected_questions} question(s)"
                        )
                    )

                else:
                    updated_count += 1

                    self.stdout.write(
                        f"Updated: "
                        f"{teacher.name} | "
                        f"{discipline.name} | "
                        f"{expected_questions} question(s)"
                    )

        # --------------------------------------------------
        # Summary
        # --------------------------------------------------

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                "Invitation import finished."
            )
        )

        self.stdout.write(
            f"Collection: {collection}"
        )

        self.stdout.write(
            f"Created: {created_count}"
        )

        self.stdout.write(
            f"Updated: {updated_count}"
        )

        self.stdout.write(
            f"Skipped: {skipped_count}"
        )