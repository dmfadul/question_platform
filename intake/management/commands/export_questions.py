import json
from pathlib import Path

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from intake.models import Collection
from intake.prova_export import (
    ProvaExportError,
    collection_to_prova,
)


class Command(BaseCommand):
    help = "Export submitted questions to Prova questions.json."

    def add_arguments(self, parser):
        parser.add_argument(
            "collection_id",
            type=int,
        )

    def handle(self, *args, **options):
        collection_id = options["collection_id"]

        try:
            collection = Collection.objects.get(
                pk=collection_id
            )
        except Collection.DoesNotExist:
            raise CommandError(
                f"Collection {collection_id} does not exist."
            )

        output_path = Path(
            f"{collection.career}.json"
        )

        try:
            data = collection_to_prova(
                collection,
            )

        except ProvaExportError as exc:
            raise CommandError(str(exc))

        with output_path.open(
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2,
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Exported questions to {output_path}"
            )
        )