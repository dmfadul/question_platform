import csv
from pathlib import Path
from django.utils.text import slugify

BASE_DIR = Path(__file__).resolve().parent


def generate_disciplines(career: str):
    csv_path = BASE_DIR / "resources" / "disciplines" / f"{career.lower()}.csv"
    disciplines = {}

    with open(
        csv_path,
        newline="",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f)
        next(reader)  # header

        for name, num_questions in reader:
            disciplines[slugify(name.strip())] = int(num_questions)

    return disciplines