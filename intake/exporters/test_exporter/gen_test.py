from dataclasses import dataclass, field
from intake.models import Discipline
from .services import shuffle_disciplines


@dataclass
class Test:
    name: str
    career: str
    disciplines: dict[str, Discipline] = field(default_factory=dict)


def generate_test(name, career, seed=42, invert_order=False) -> Test:
    test = Test(name=name, career=career)

    # find correct disciplines for the career
    career_disciplines = []
    disciplines = shuffle_disciplines(career_disciplines, seed=seed)
    disciplines = disciplines[::-1] if invert_order else disciplines


    return test