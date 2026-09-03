# on the next version, this file functionality
# should be integrated into the main models

from dataclasses import dataclass, field
from typing import List


@dataclass
class Test:
    name: str
    career: str
    disciplines: list = field(default_factory=list)
    has_images: bool = False

    def add_discipline(self, discipline):
        if discipline in self.disciplines:
            return False
        
        current_position = sum(d.num_questions for d in self.disciplines)
        discipline.starting_position = current_position + 1

        self.disciplines.append(discipline)
        return True
    
    def set_questions_abs_pos(self):
        for discipline in self.disciplines:
            for question in discipline.questions:
                question.abs_pos = discipline.starting_position + question.relative_position - 1

    def fill_empty_questions(self):
        for discipline in self.disciplines:
            discipline.fill_empty_questions()

    def set_has_images(self):
        for d in self.disciplines:
            d.set_has_images()
        self.has_images = any(d.has_images for d in self.disciplines)

        return self.has_images

@dataclass
class Discipline_dataclass:
    name: str
    num_questions: int
    questions: list[Question_dataclass] = field(default_factory=list)
    starting_position: int = 0 # the number of the first question in this discipline, in the test
    has_images: bool = False

    def add_question(self, question):
        if len(self.questions) >= self.num_questions:
            return False

        question.relative_position = len(self.questions) + 1
        self.questions.append(question)

        return True

    def fill_empty_questions(self):
        while len(self.questions) < self.num_questions:
            empty_question = Question_dataclass.gen_empty()
            self.add_question(empty_question)

    def set_has_images(self):
        for q in self.questions:
            q.set_has_images()
        self.has_images = any(q.has_images for q in self.questions)

        return self.has_images

@dataclass
class Question_dataclass:
    body: str
    choice_a: str
    choice_b: str
    choice_c: str
    choice_d: str
    choice_e: str
    correct_choice: str
    relative_position: int = 0
    abs_pos: int = 0
    has_images: bool = False

    question_image: str | None = None
    choice_a_image: str | None = None
    choice_b_image: str | None = None
    choice_c_image: str | None = None
    choice_d_image: str | None = None
    choice_e_image: str | None = None

    def set_has_images(self):
        self.has_images = any((
            self.question_image,
            self.choice_a_image,
            self.choice_b_image,
            self.choice_c_image,
            self.choice_d_image,
            self.choice_e_image,
        ))

        return self.has_images

    @classmethod
    def gen_empty(cls):
        return cls(
            body="[A questão não possui enunciado]",
            choice_a="[Opção indisponível]",
            choice_b="[Opção indisponível]",
            choice_c="[Opção indisponível]",
            choice_d="[Opção indisponível]",
            choice_e="[Opção indisponível]",
            correct_choice="[Resposta indisponível]",
        )