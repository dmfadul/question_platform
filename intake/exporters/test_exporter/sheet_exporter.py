from copy import copy
from pathlib import Path

from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Font, Alignment


def get_answers(test):
    answers = {}

    for discipline in test.disciplines:
        for question in discipline.questions:
            answers[
                question.abs_pos
            ] = question.correct_choice

    return answers



ANSWER_SHEET_TEMPLATE = "resources/template_gabarito.xlsx"

OUTPUT_DIR = Path("tests_output")


SHEET_MAP = {
    ("APJ", "A"): "apj - a",
    ("APJ", "B"): "apj - b",

    ("PAP", "A"): "pap",
    ("PAP", "B"): "pap",

    ("DEL", "A"): "del",
    ("DEL", "B"): "del",

    ("APJ", "S"): "apj - s",
    ("PAP", "S"): "pap S",
    ("DEL", "S"): "del - S",
}

ANSWER_ROW_OFFSET = {
    "A": 0,
    "B": 1,
    "C": 2,
    "D": 3,
    "E": 4,
}


def get_answer_cell(question_number, answer):
    answer = answer.upper()

    if answer not in ANSWER_ROW_OFFSET:
        raise ValueError(
            f"Invalid answer: {answer}"
        )

    if not 1 <= question_number <= 100:
        raise ValueError(
            f"Invalid question number: {question_number}"
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