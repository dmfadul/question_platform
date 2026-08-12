import csv

from django.utils.text import slugify


CSV_FILES = [
    "files/apj18.csv",
    "files/pap23.csv",
    "files/del47.csv",
]


def read_csv(path):
    with open(
        path,
        "r",
        encoding="utf-8-sig",
        newline="",
    ) as file:
        reader = csv.DictReader(file)

        for row in reader:
            yield {
                key.strip(): value.strip()
                if isinstance(value, str)
                else value
                for key, value in row.items()
            }


def generate_teacher_email(name):
    """
    Maria da Silva -> maria-da-silva@test.com
    João Antônio -> joao-antonio@test.com
    """

    return f"{slugify(name)}@test.com"


def generate_discipline_code(name):
    return slugify(name)