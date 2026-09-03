from docxtpl import DocxTemplate
from .image_manager import prepare_image
from .services import shuffle_disciplines
from .formatting import tinymce_to_plain_text
from intake.models import Collection
from .dataclass_models import (
    Test,
    Discipline_dataclass,
    Question_dataclass,
)
from docxtpl import DocxTemplate, InlineImage
from docx.shared import Mm


# In next version, this career, not cohort will be in the models
# this map will no longer be needed.
CAREER_COHORTS_MAP = {
    "APJ": "APJ18",
    "PAP": "PAP23",
    "DEL": "DEL47",
}

CAREER_ABR_MAP = {
    "APJ": "AGENTE DE POLICIA JUDICIÁRIA",
    "PAP": "PAPILOSCOPISTA POLICIAL",
    "DEL": "DELEGADO DE POLÍCIA",
}


TEMPLATE_PATH = "resources/test_template.docx"
IMG_TEMPLATE_PATH = "resources/image_template.docx"

def generate_test(
    name,
    career,
    seed=42,
    invert_question_order=False,
) -> Test:
    output_path = f"tests_output/PROVA_{career}-{name}.docx"
    img_output_path = (
        f"tests_output/PROVA_{career}-{name}_images.docx"
    )

    test = Test(
        name=name,
        career=career,
    )

    collection = Collection.objects.filter(
        title=CAREER_COHORTS_MAP[career]
    ).first()

    invitations = list(
        collection.invitations
        .select_related("discipline")
        .order_by("discipline__name")
    )

    invitations = shuffle_disciplines(
        invitations,
        seed=seed,
    )

    for invitation in invitations:
        discipline_dc = Discipline_dataclass(
            name=invitation.discipline.name,
            num_questions=invitation.number_of_questions(),
        )

        questions_in_invitation = list(
            invitation.questions.all()
        )

        if invert_question_order:
            questions_in_invitation.reverse()

        for question in questions_in_invitation:
            options = list(question.options.all())

            question_image = prepare_image(
                question.image,
                f"question_{question.pk}",
            )

            choice_a_image = prepare_image(
                options[0].image,
                f"question_{question.pk}_option_1",
            )

            choice_b_image = prepare_image(
                options[1].image,
                f"question_{question.pk}_option_2",
            )

            choice_c_image = prepare_image(
                options[2].image,
                f"question_{question.pk}_option_3",
            )

            choice_d_image = prepare_image(
                options[3].image,
                f"question_{question.pk}_option_4",
            )

            choice_e_image = prepare_image(
                options[4].image,
                f"question_{question.pk}_option_5",
            )

            choice_e = tinymce_to_plain_text(
                options[4].text,
                choice_e_image,
            )

            if not choice_e:
                choice_e = "Nenhuma das alternativas acima"

            correct_option = next(
                option
                for option in options
                if option.is_correct
            )

            question_dc = Question_dataclass(
                body=tinymce_to_plain_text(
                    question.body,
                    question_image,
                ),
                choice_a=tinymce_to_plain_text(
                    options[0].text,
                    choice_a_image,
                ),
                choice_b=tinymce_to_plain_text(
                    options[1].text,
                    choice_b_image,
                ),
                choice_c=tinymce_to_plain_text(
                    options[2].text,
                    choice_c_image,
                ),
                choice_d=tinymce_to_plain_text(
                    options[3].text,
                    choice_d_image,
                ),
                choice_e=choice_e,
                correct_choice=correct_option.letter,
                question_image=question_image,
                choice_a_image=choice_a_image,
                choice_b_image=choice_b_image,
                choice_c_image=choice_c_image,
                choice_d_image=choice_d_image,
                choice_e_image=choice_e_image,
            )

            discipline_dc.add_question(question_dc)

        test.add_discipline(discipline_dc)

    # Finalize the test only after all disciplines have been added.
    test.fill_empty_questions()
    test.set_questions_abs_pos()
    test.set_has_images()

    context = {
        "name": test.name,
        "career": test.career,
        "test": test.disciplines,
        "career_name": CAREER_ABR_MAP[career],
    }

    # Generate the main test document.
    doc = DocxTemplate(TEMPLATE_PATH)
    doc.render(context)
    doc.save(output_path)

    # Generate the separate image document.
    if test.has_images:
        image_doc = DocxTemplate(IMG_TEMPLATE_PATH)
        image_disciplines = []

        for discipline in test.disciplines:
            if not discipline.has_images:
                continue

            image_items = []

            for question in discipline.questions:
                if not question.has_images:
                    continue

                images = [
                    (None, question.question_image),
                    ("A", question.choice_a_image),
                    ("B", question.choice_b_image),
                    ("C", question.choice_c_image),
                    ("D", question.choice_d_image),
                    ("E", question.choice_e_image),
                ]

                for option, image_path in images:
                    if not image_path:
                        continue

                    image_items.append({
                        "question_number": question.abs_pos,
                        "option": option,
                        "image": InlineImage(
                            image_doc,
                            image_path,
                            width=Mm(150),
                        ),
                    })

            if image_items:
                image_disciplines.append({
                    "name": discipline.name,
                    "images": image_items,
                })

        image_context = {
            **context,
            "image_disciplines": image_disciplines,
        }

        image_doc.render(image_context)
        image_doc.save(img_output_path)

    return test