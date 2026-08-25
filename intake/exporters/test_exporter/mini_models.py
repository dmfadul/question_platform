# on the next version, this file functionality
# should be integrated into the main models

from dataclasses import dataclass, field
from typing import List
from intake.models import (
    Collection,
    Discipline,
    Question
)


@dataclass
class Test:
    name: str
    career: str
    disciplines: dict[str, Discipline] = field(default_factory=dict)


@dataclass
class DisciplineQuestion:
    question: Question
    position: int
    

@dataclass
class Discipline:
    name: str
    num_questions: int
    questions: list[DisciplineQuestion] = field(default_factory=list)
    starting_position: int = 0 # the number of the first question in this discipline, in the test

    def add_question(self, question):       
        if len(self.questions) >= self.num_questions:
            return False
        
        self.questions.append(
            DisciplineQuestion(
                question=question,
                position=len(self.questions) + 1,
            )
        )

        return True
