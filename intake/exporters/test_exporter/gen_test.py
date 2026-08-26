from docx import Document
from docx.oxml.ns import qn
from docxtpl import DocxTemplate
from docx.oxml import OxmlElement

from .services import shuffle_disciplines
from intake.models import (
    Collection,
    Discipline,
)
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
    output_path = f"output/PROVA_{career}-{name}.docx"
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
            question_dc = Question_dataclass(
                body=question.body,
                choice_a=options[0].text,
                choice_b=options[1].text,
                choice_c=options[2].text,
                choice_d=options[3].text,
                choice_e=options[4].text,
                correct_choice=options.get(is_correct=True).letter,
            )
            discipline_dc.add_question(question_dc)
        
        test.add_discipline(discipline_dc)
        test.set_questions_abs_pos()

        doc = DocxTemplate(TEMPLATE_PATH)

        return True





    return test