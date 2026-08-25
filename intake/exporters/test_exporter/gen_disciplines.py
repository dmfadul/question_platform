import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent


def generate_disciplines(career: str):
    csv_path = BASE_DIR / "resources" / "disciplines" / f"{career.lower()}.csv"
    disciplines = []

    with open(
        csv_path,
        newline="",
        encoding="utf-8",
    ) as f:
        reader = csv.reader(f)
        next(reader)  # header

        for name, num_questions in reader:
            print(f"Discipline: {name}, Number of Questions: {num_questions}")
    #     for name, dele, apj, pap in reader:
    #         disciplines.append(
    #             Discipline(
    #                 name=name.strip(),
    #                 del_num_questions=int(dele),
    #                 apj_num_questions=int(apj),
    #                 pap_num_questions=int(pap),
    #                 questions=[],
    #             )
    #         )

    # return disciplines