from dataclasses import dataclass, field
from .services import shuffle_disciplines
from intake.models import (
    Collection,
    Discipline,
)


# In next version, this career, not cohort will be in the models
# this map will no longer be needed.
CAREER_COHORTS_MAP = {
    "APJ": "APJ18",
    "PAP": "PAP23",
    "DEL": "DEL47",
}

@dataclass
class Test:
    name: str
    career: str
    disciplines: dict[str, Discipline] = field(default_factory=dict)


def generate_test(name, career, seed=42, invert_question_order=False) -> Test:
    test = Test(name=name, career=career)

    collection = Collection.objects.filter(title=CAREER_COHORTS_MAP[career]).first()
    print("collection", collection)


    career_disciplines = []
    disciplines = shuffle_disciplines(career_disciplines, seed=seed)



    return test