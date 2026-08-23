import json
from pathlib import Path
import shutil

from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from intake.models import Collection
from intake.exporters import (
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

        parser.add_argument(
            "--output-dir",
            default="prova_export",
        )

    def handle(self, *args, **options):
        collection_id = options["collection_id"]

        output_dir = Path(options["output_dir"])

        images_dir = output_dir / "images"

        try:
            collection = Collection.objects.get(
                pk=collection_id
            )
        except Collection.DoesNotExist:
            raise CommandError(
                f"Collection {collection_id} does not exist."
            )

        # Start with a clean export directory.
        if output_dir.exists():
            shutil.rmtree(output_dir)        

        images_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:
            data = collection_to_prova(
                collection,
                images_dir,
            )

        except ProvaExportError as exc:
            raise CommandError(str(exc))
        
        questions_path = Path(
            output_dir / f"{collection.career}.json"
        )


        with questions_path.open(
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
                f"Export created at: "
                f"{output_dir.resolve()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Questions: "
                f"{questions_path.resolve()}"
            )
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Images: "
                f"{images_dir.resolve()}"
            )
        )