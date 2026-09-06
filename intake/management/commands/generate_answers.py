from django.core.management.base import BaseCommand

from intake.exporters.test_exporter.sheet_exporter import get_answers


class Command(BaseCommand):
    help = "Generate an answer sheet."

    def handle(self, *args, **options):
        get_answers()