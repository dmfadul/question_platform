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
def generate_test(name, career, seed=42, invert_question_order=False) -> Test:
    output_path = f"tests_output/PROVA_{career}-{name}.docx"
    test = Test(name=name, career=career)

    collection = Collection.objects.filter(title=CAREER_COHORTS_MAP[career]).first()
    invitations = list(
        collection.invitations
        .select_related("discipline")
        .order_by("discipline__name")
    )

    invitations = shuffle_disciplines(invitations, seed=seed)
    for invitation in invitations:
        discipline_dc = Discipline_dataclass(
            name=invitation.discipline.name,
            num_questions=invitation.number_of_questions(),
        )

        questions_in_invitation = invitation.questions.all()
        if invert_question_order:
            questions_in_invitation = reversed(questions_in_invitation)

        for question in questions_in_invitation:
            # maybe a good place to convert the tinyMCE content to plain text
            options = question.options.all()
            choice_e = tinymce_to_plain_text(options[4].text)
            if not choice_e:
                # print(f"question {question.pk}: choice e is empty, setting to default value")
                choice_e = "Nenhuma das alternativas acima"

            question_image=prepare_image(question.image, f"question_{question.pk}")
            choice_a_image=prepare_image(options[0].image, f"question_{question.pk}_option_1")
            choice_b_image=prepare_image(options[1].image, f"question_{question.pk}_option_2")
            choice_c_image=prepare_image(options[2].image, f"question_{question.pk}_option_3")
            choice_d_image=prepare_image(options[3].image, f"question_{question.pk}_option_4")
            choice_e_image=prepare_image(options[4].image, f"question_{question.pk}_option_5")

            question_dc = Question_dataclass(
                body=tinymce_to_plain_text(question.body, question_image),
                choice_a=tinymce_to_plain_text(options[0].text, choice_a_image),
                choice_b=tinymce_to_plain_text(options[1].text, choice_b_image),
                choice_c=tinymce_to_plain_text(options[2].text, choice_c_image),
                choice_d=tinymce_to_plain_text(options[3].text, choice_d_image),
                choice_e=choice_e,
                correct_choice=options.get(is_correct=True).letter,

                question_image=question_image,
                choice_a_image=choice_a_image,
                choice_b_image=choice_b_image,
                choice_c_image=choice_c_image,
                choice_d_image=choice_d_image,
                choice_e_image=choice_e_image,
            )
            
            discipline_dc.add_question(question_dc)
        
        test.add_discipline(discipline_dc)
        test.fill_empty_questions()
        test.set_questions_abs_pos()

    context = {
        "name": test.name,
        "career": test.career,
        "test": test.disciplines,
        "career_name": CAREER_ABR_MAP[career],
    }
    
    doc = DocxTemplate(TEMPLATE_PATH)
    doc.render(context)
    doc.save(output_path)
    
    return True