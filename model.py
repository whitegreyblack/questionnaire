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
        self.answers = [answer for answer, _ in data['answers']]
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
            ]
        }
