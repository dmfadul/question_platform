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
    questions: List
    str_pos: int = 0

    def add_question(self, question):       
        if len(self.questions) >= self.num_questions:
            return False
        
        if isinstance(question, Question):
            question.set_rel_pos(len(self.questions) + 1)
        self.questions.append(question)
        return 0
