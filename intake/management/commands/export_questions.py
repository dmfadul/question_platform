from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management.base import (
    BaseCommand,
    CommandError,
)

from intake.exporters.text_export import (
    export_collections,
)
from intake.models import Collection


class Command(BaseCommand):
    help = (
        "Export submitted questions "
        "and associated images."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--collections",
            nargs="+",
            type=int,
            required=True,
        )

    def handle(self, *args, **options):

        ids = options["collections"]

        collections = Collection.objects.filter(
            pk__in=ids
        ).order_by("pk")

        if collections.count() != len(ids):
            raise CommandError(
                "One or more collection IDs do not exist."
            )

        timestamp = datetime.now().strftime(
            "%Y-%m-%d_%H%M%S"
        )

        export_dir = (
            Path(settings.BASE_DIR)
            / "exports"
            / timestamp
        )

        export_collections(
            collections,
            export_dir,
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Export created at:\n"
                f"{export_dir}"
            )
        )