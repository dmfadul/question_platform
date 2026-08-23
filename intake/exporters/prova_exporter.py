from intake.models import Question


CHOICE_LETTERS = ["A", "B", "C", "D", "E"]


class ProvaExportError(Exception):
    pass


def question_to_prova(question, cohort):
    options = list(
        question.options.order_by("position")
    )

    if len(options) < 4:
        raise ProvaExportError(
            f"Question {question.pk} has {len(options)} options. "
            "Prova requires at least 4."
        )
    
    correct_options = [
        option
        for option in options
        if option.is_correct
    ]

    if len(correct_options) != 1:
        raise ProvaExportError(
            f"Question {question.pk} must have exactly "
            f"one correct option."
        )

    correct_option = correct_options[0]

    try:
        correct_index = options.index(correct_option)
    except ValueError:
        raise ProvaExportError(
            f"Could not determine the correct option "
            f"for question {question.pk}."
        )

    correct_choice = CHOICE_LETTERS[correct_index]

    return {
        "discipline": question.invitation.discipline,

        # KEEP THE ORIGINAL TINYMCE HTML
        "body": question.body,

        "choice_a": options[0].text,
        "choice_b": options[1].text,
        "choice_c": options[2].text,
        "choice_d": options[3].text,
        "choice_e": options[4].text,

        "correct_choice": correct_choice,

        # Now contains ONLY this question's cohort
        "cohorts": [
            cohort,
        ],

        "rel_pos": 0,
        "abs_pos": 0,
    }


def collection_to_prova(collection, cohort):
    questions = (
        Question.objects
        .filter(
            invitation__collection=collection,
            status=Question.Status.SUBMITTED,
        )
        .select_related(
            "invitation",
            "invitation__collection",
        )
        .prefetch_related("options")
        .order_by(
            "invitation__discipline",
            "id",
        )
    )

    return {
        cohort: [
            question_to_prova(
                question,
                cohort,
            )
            for question in questions
        ]
    }