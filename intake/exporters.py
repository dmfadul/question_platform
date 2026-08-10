from pathlib import Path
from .models import Question


def get_submitted_questions(collection=None):
    qs = (
        Question.objects
        .filter(status=Question.Status.SUBMITTED)
        .select_related(
            "invitation",
            "invitation__collection",
        )
        .prefetch_related("options")
        .order_by(
            "invitation__discipline",
            "invitation__teacher__name",
            "id",
        )
    )

    if collection is not None:
        qs = qs.filter(
            invitation__collection=collection,
        )

    return [
        question_to_dict(question)
        for question in qs
    ]


def question_to_dict(question):
    return {
        "id": question.id,

        "collection": {
            "id": question.invitation.collection_id,
            "title": question.invitation.collection.title,
        },

        "teacher": {
            "name": question.invitation.teacher.name,
            "email": question.invitation.teacher.email,
        },

        "discipline": {
            "name": question.invitation.discipline.name,
            "code": question.invitation.discipline.code,
        },

        "body": question.body,

        "image": (
            question.image.url
            if question.image
            else None
        ),

        "image_path": (
            question.image.path
            if question.image
            else None
        ),

        "notes": question.teacher_notes,

        "options": [
            {
                "id": option.id,
                "position": option.position,
                "text": option.text,
                "is_correct": option.is_correct,

                "image": (
                    option.image.url
                    if option.image
                    else None
                ),

                "image_path": (
                    option.image.path
                    if option.image
                    else None
                ),
            }
            for option in question.options.all()
        ],
    }