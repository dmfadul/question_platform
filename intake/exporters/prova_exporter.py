from intake.models import Question
from pathlib import Path
import shutil


CHOICE_LETTERS = ["A", "B", "C", "D", "E"]


class ProvaExportError(Exception):
    pass


def content_with_image(text, image_src=None):
    """
    Keep the original TinyMCE HTML and append an image,
    if one exists.
    """
    text = text or ""

    if not image_src:
        return text

    image_html = (
        '<p class="question-image">'
        f'<img src="{image_src}" alt="">'
        '</p>'
    )

    return f"{text}{image_html}"


def get_image_extension(image):
    """
    Preserve the extension of the uploaded image.
    """
    suffix = Path(image.name).suffix.lower()

    if not suffix:
        raise ProvaExportError(
            f"Image '{image.name}' has no file extension."
        )

    return suffix


def copy_image(image, destination, filename):
    """
    Copy a Django ImageField file to the Prova export folder.

    Uses Django's storage API, so this does not depend on
    the file being stored locally.
    """
    destination.mkdir(
        parents=True,
        exist_ok=True,
    )

    output_path = destination / filename

    image.open("rb")

    try:
        with output_path.open("wb") as output_file:
            shutil.copyfileobj(
                image.file,
                output_file,
            )
    finally:
        image.close()

    return output_path

def export_question_image(question, images_dir):
    if not question.image:
        return None

    extension = get_image_extension(
        question.image,
    )

    filename = (
        f"question_{question.pk}"
        f"{extension}"
    )

    copy_image(
        question.image,
        images_dir,
        filename,
    )

    return f"images/{filename}"


def export_option_image(
    question,
    option,
    images_dir,
):
    if not option.image:
        return None

    extension = get_image_extension(
        option.image,
    )

    filename = (
        f"question_{question.pk}"
        f"_option_{option.position}"
        f"{extension}"
    )

    copy_image(
        option.image,
        images_dir,
        filename,
    )

    return f"images/{filename}"


def question_to_prova(
    question,
    career,
    images_dir,
):
    options = list(
        question.options.order_by("position")
    )

    if len(options) != 5:
        raise ProvaExportError(
            f"Question {question.pk} has "
            f"{len(options)} options. "
            "Prova requires exactly 5."
        )

    correct_options = [
        option
        for option in options
        if option.is_correct
    ]

    if len(correct_options) != 1:
        raise ProvaExportError(
            f"Question {question.pk} must have "
            "exactly one correct option."
        )

    correct_option = correct_options[0]
    correct_index = options.index(
        correct_option,
    )

    question_image_src = export_question_image(
        question,
        images_dir,
    )

    option_image_srcs = [
        export_option_image(
            question,
            option,
            images_dir,
        )
        for option in options
    ]

    return {
        "discipline": (
            question.invitation.discipline
        ),

        "body": content_with_image(
            question.body,
            question_image_src,
        ),

        "choice_a": content_with_image(
            options[0].text,
            option_image_srcs[0],
        ),

        "choice_b": content_with_image(
            options[1].text,
            option_image_srcs[1],
        ),

        "choice_c": content_with_image(
            options[2].text,
            option_image_srcs[2],
        ),

        "choice_d": content_with_image(
            options[3].text,
            option_image_srcs[3],
        ),

        "choice_e": content_with_image(
            options[4].text,
            option_image_srcs[4],
        ),

        "correct_choice": (
            CHOICE_LETTERS[correct_index]
        ),

        "cohorts": [career],

        "rel_pos": 0,
        "abs_pos": 0,
    }


def collection_to_prova(collection, images_dir):
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
        collection.career: [
            question_to_prova(
                question,
                collection.career,
                images_dir,
            )
            for question in questions
        ]
    }
