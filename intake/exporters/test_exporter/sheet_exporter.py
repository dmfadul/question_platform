from copy import copy
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment


TEMPLATE_PATH = "resources/template_gabarito.xlsx"
OUTPUT_DIR = Path("gabaritos_output")

CAREER_ABR_MAP = {
    "APJ": "AGENTE DE POLÍCIA JUDICIÁRIA",
    "PAP": "PAPILOSCOPISTA POLICIAL",
    "DEL": "DELEGADO DE POLÍCIA",
}

ANSWER_ROW_OFFSET = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
}

CORRECT_FILL = PatternFill(
    fill_type="solid",
    fgColor="000000",
)

CORRECT_FONT = Font(
    color="FFFFFF",
    bold=True,
)


def generate_gabarito(test, career, test_type):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    workbook = load_workbook(TEMPLATE_PATH)
    ws = workbook["sheet1"]

    replace_template_values(ws, career, test_type)

    mark_answers(ws, test)

    ws.title = (f"{career}-{test_type}")

    output_path = (
        OUTPUT_DIR
        / f"GABARITO_{career}-{test_type}.xlsx"
    )

    workbook.save(output_path)
    return output_path


def replace_template_values(ws, career, test_type):
    replacements = {
        "{career_name}": CAREER_ABR_MAP[career],
        "{test_type}": test_type,
    }

    for row in ws.iter_rows():
        for cell in row:
            if not isinstance(cell.value, str):
                continue

            value = cell.value

            for placeholder, replacement in replacements.items():
                value = value.replace(
                    placeholder,
                    replacement,
                )

            cell.value = value


def mark_answers(ws, test):
    answers = get_answers(test)

    for question_number, answer in answers.items():

        row, column = get_answer_cell(
            question_number,
            answer,
        )

        cell = ws.cell(
            row=row,
            column=column,
        )

        cell.fill = CORRECT_FILL
        cell.font = CORRECT_FONT
        cell.alignment = Alignment(
            horizontal="center",
            vertical="center",
        )


def get_answer_cell(question_number, answer):
    """
    Return (row, column) for a question's correct answer.
    """

    answer = answer.upper()

    if answer not in ANSWER_ROW_OFFSET:
        raise ValueError(
            f"Invalid answer '{answer}' "
            f"for question {question_number}"
        )

    if not 1 <= question_number <= 100:
        raise ValueError(
            f"Invalid question number: "
            f"{question_number}"
        )

    # Questions 1–33
    if question_number <= 33:
        column = question_number + 2
        base_row = 24

    # Questions 34–66
    elif question_number <= 66:
        column = question_number - 34 + 3
        base_row = 32

    # Questions 67–100
    else:
        column = question_number - 67 + 3
        base_row = 40

    row = (
        base_row
        + ANSWER_ROW_OFFSET[answer]
    )

    return row, column


def get_answers(test):
    answers = {}

    for discipline in test.disciplines:
        for question in discipline.questions:
            answers[
                question.abs_pos
            ] = question.correct_choice

    return answers


