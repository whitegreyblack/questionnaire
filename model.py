# model.py

"""Holds Question and Answer classes"""

import random
from dataclasses import dataclass, field


class Question:

    question_id = 1

    def __init__(self, data, shuffle):
        self.question_id = Question.question_id
        Question.question_id += 1
        self.question = data['question_before']
        self.code = data['question_code']
        self.additional = data['question_after']

        if shuffle:
            random.shuffle(data['answers'])

        # holds all possible answers to the question
        self.answers = [answer for answer, _ in data['answers']]

        # holds only the correct answer combination to the question
        self.answer = [
                i for i, (_, correct) in enumerate(data['answers'])
                    if correct
            ]
        self.answered = False
        self.correct = False

    def __repr__(self):
        return f"Question({self.question_id})"

@dataclass
class AnswerBuilder:
    text: str
    correct: bool = False
    def serialize(self):
        return [ self.text, self.correct ]

@dataclass
class QuestionBuilder:

    before: list = field(default_factory=list)
    after: list = field(default_factory=list)
    code: list = field(default_factory=list)
    answers: list = field(default_factory=list)

    @property
    def empty(self):
        return all(not l for l in [self.before, self.after, self.code, self.answers])
    def clear(self):
        self.before.clear()
        self.after.clear()
        self.code.clear()
        self.answers.clear()

    def set_correct_answers(self, answer: str):
        answers = [ord(a.strip()) - 97 for a in answer.split(',')]
        for i, answer in enumerate(self.answers):
            answer.correct = i in answers

    def serialize(self):
        return {
            'question_before': ' '.join(self.before),
            'question_after': ' '.join(self.after),
            'question_code': [
                c for c in self.code
            ],
            'answers': [
                answer.serialize() for answer in self.answers
            ],
            'answer_why': None
        }

class QuestionId:
    def __init__(self, number, symbol):
        self.number = number
        self.symbol = symbol
    
    def __repr__(self):
        return f"{self.number.value}{self.symbol.value}"

class QuestionStatement:
    def __init__(self, statement):
        self.statement = statement
    def __repr__(self):
        return self.statement

# class CodeStatement:
#     ...

# class QuestionContinueStatement:
#     ...

class QuestionBlock:
    def __init__(self, question_id, statement, choices, answers):
        self.qid = question_id
        self.statement = statement
        self.choices = choices
        self.answers = answers

    def __repr__(self):
        return f"{self.qid} number of choices: {len(self.choices)}"
    
    def preview(self):
        choices = "\n    ".join(str(choice) for choice in self.choices)
        return f"""
{self.qid} {self.statement}
    {choices}
A. ({self.answers})"""[1:]

class AnswerStatement:
    def __init__(self, answers):
        self.answers = answers
    def __repr__(self):
        return ", ".join(str(choice) for choice in self.answers)

class ChoiceId:
    def __init__(self, letter, symbol):
        self.letter = letter
        self.symbol = symbol
    def __repr__(self):
        return f"{self.letter.value}{self.symbol.value}"

class ChoiceStatement:
    def __init__(self, choice_id, statement):
        self.choice_id = choice_id
        self.statement = statement
    def __repr__(self):
        return f"{self.choice_id} {self.statement}"