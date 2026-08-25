from dataclasses import dataclass, field
from intake.models import Discipline


@dataclass
class Test:
    name: str
    cohort: str
    disciplines: dict[str, Discipline] = field(default_factory=dict)
