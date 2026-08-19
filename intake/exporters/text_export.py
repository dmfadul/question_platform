import html
import shutil

from pathlib import Path
from django.utils.html import strip_tags
from intake.models import Question


def export_collections(
    collections,
    export_dir,
):
    export_dir.mkdir(
        parents=True,
        exist_ok=True,
    )

    image_dir = export_dir / "images"

    image_dir.mkdir(
        exist_ok=True,
    )

    for collection in collections:

        filename = (
            f"collection_{collection.pk}.txt"
        )

        output_file = (
            export_dir / filename
        )

        export_collection(
            collection,
            output_file,
            image_dir,
        )
        

def export_collection(
    collection,
    output_file,
    image_dir,
):
    questions = (
        Question.objects
        .filter(
            invitation__collection=collection,
            status=Question.Status.SUBMITTED,
        )
        .select_related(
            "invitation",
            "invitation__discipline",
        )
        .prefetch_related(
            "options",
        )
        .order_by(
            "invitation__discipline__name",
            "pk",
        )
    )

    current_discipline = None

    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:

        for question in questions:

            discipline = (
                question
                .invitation
                .discipline
                .name
            )

            if discipline != current_discipline:
                if current_discipline is not None:
                    f.write("\n\n")

                f.write(
                    "=" * 70
                )

                f.write(
                    f"\nDISCIPLINA: {discipline}\n"
                )

                f.write(
                    "=" * 70
                )

                f.write("\n\n")

                current_discipline = discipline

            f.write(
                format_question(
                    question,
                    image_dir,
                )
            )

            f.write("\n\n\n")


def format_question(question, image_dir):
    lines = []

    lines.append(
        f"[QUESTION:{question.pk}]"
    )

    lines.append("")

    lines.append(
        html_to_text(question.body)
    )

    if question.image:
        filename = export_image(
            question.image,
            question_image_code(question),
            image_dir,
        )

        lines.append("")
        lines.append(
            f"[IMAGE:{filename}]"
        )

    lines.append("")

    correct_letter = None

    for option in question.options.all():
        letter = chr(
            ord("A") + option.position - 1
        )

        text = html_to_text(option.text)

        lines.append(
            f"{letter}) {text}"
        )

        if option.image:
            filename = export_image(
                option.image,
                option_image_code(
                    question,
                    option,
                ),
                image_dir,
            )

            lines.append(
                f"[IMAGE:{filename}]"
            )

        if option.is_correct:
            correct_letter = letter

    lines.append("")

    if correct_letter:
        lines.append(
            f"[CORRECT:{correct_letter}]"
        )

    return "\n".join(lines)


def export_image(image_field, code, image_dir):
    if not image_field:
        return None

    source = Path(image_field.path)

    extension = source.suffix.lower()

    filename = f"{code}{extension}"

    destination = image_dir / filename

    shutil.copy2(
        source,
        destination,
    )

    return code


def html_to_text(value):
    if not value:
        return ""

    return html.unescape(
        strip_tags(value)
    ).strip()


def question_image_code(question):
    return f"Q{question.pk:04d}_BODY"


def option_image_code(question, option):
    letter = chr(ord("A") + option.position - 1)

    return f"Q{question.pk:04d}_OPTION_{letter}"
