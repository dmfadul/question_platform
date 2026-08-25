from django.core.management.base import BaseCommand

from intake.exporters.test_exporter.runner import main


class Command(BaseCommand):
    help = "Generate a test."

    def handle(self, *args, **options):
        main()