from .services import shuffle_disciplines
from intake.models import (
    Collection,
    Discipline,
)
from .dataclass_models import (
    Test,
    Discipline_dataclass,
)


# In next version, this career, not cohort will be in the models
# this map will no longer be needed.
CAREER_COHORTS_MAP = {
    "APJ": "APJ18",
    "PAP": "PAP23",
    "DEL": "DEL47",
}

def generate_test(name, career, seed=42, invert_question_order=False) -> Test:
    test = Test(name=name, career=career)

    collection = Collection.objects.filter(title=CAREER_COHORTS_MAP[career]).first()
    invitations = list(
        collection.invitations
        .select_related("discipline")
        .order_by("discipline__name")
    )

    invitations = shuffle_disciplines(invitations, seed=seed)
    for invitation in invitations:
        questions_in_invitation = invitation.questions.all()
        if invert_question_order:
            questions_in_invitation = reversed(questions_in_invitation)

        for question in questions_in_invitation:
            # maybe a good place to convert the tinyMCE content to plain text
            Discipline_dataclass(
                
            )
            print(question.body[:50])




    return test