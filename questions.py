# questions.py

"""Questionnaire application"""
   
import sys
import json
import pprint
import random
import textwrap
import os


q_sort = False
verbose = False
show_answer = False
file_import = "./questions.json"

width, height = os.get_terminal_size()
y_offset = ((height - 24) // 2) if height > 24 else 0
x_offset = ((width - 80) // 2) if width > 80 else 0
x_indent = " " * x_offset

class Question:
    question_id = 1
    def __init__(self, data):
        self.question_id = Question.question_id
        Question.question_id += 1
        self.question = data['question']
        self.answers = data['answers']
        self.answer = data['answer']
        self.answered = False
        self.correct = False
    def __repr__(self):
        return f"Question({self.question_id})"

def print_results(questions):
    if all(not q.answered for q in questions):
        return
    correct = sum(int(q.answered and q.correct) for q in questions)
    answered = sum(int(q.answered) for q in questions)
    total = len(questions)
    clear_screen()
    if verbose:
        print("Incorrect:")
        print('\n'.join(
            str(q.question_id)
                for q in questions 
                    if q.answered and not q.correct)
            )
    print(f"{correct}/{answered} questions ({correct/answered*100:.2f}%)")
    print(f"{correct}/{total} questions ({correct/total*100:.2f}%)")

def ask_question(question, question_id):
    indent = "  "
    qid = question.question_id if not q_sort else question_id
    text = [
        f"{x_indent}{str(qid)+'.' if i<1 else indent} {s}"
            for i, s in enumerate(
                textwrap.wrap(question.question, 80-len(indent)-2)
            )
        ]
    text.append('')
    # TODO: randomize answers within a question
    # save the full answer text to find index later after randomization
    # answer = question.answers[question.answer]
    # random.shuffle(question.answers)
    # question.answer = question.answers.indexof(answer)
    for i, answer in enumerate(question.answers):
        for j, s in enumerate(textwrap.wrap(answer, 80-len(indent*2)-2)):
            text.append(f"{x_indent}{indent*2}{chr(i+97)+'.' if j<1 else '  '} {s}")
        text.append('')
    # output question and answer format
    print('\n'.join(' ' for _ in range(y_offset)))
    print('\n'.join(text))
    print()

def build_valid_answer_set(question):
    return ''.join(chr(97+i) for i in range(len(question.answers)))

def check_valid_input(question, answer):
    answers = build_valid_answer_set(question)
    valid = all(ch in answers for ch in answer)
    if not valid:
        print(f"{x_indent}Invalid input: must be in [{', '.join(answers)}]")
    return valid

def check_valid_answer_length(question, answer):
    valid = len(answer) == len(question.answer)
    if not valid:
        print(f"{x_indent}Choose {len(question.answer)} answers")
    return valid

def check_correct_answer(question, answer):
    return set(question.answer) == set(ord(ch)-97 for ch in answer)

def handle_input(question):
    while True:
        try:
            answer = input(f"{x_indent}>>> ")
        except KeyboardInterrupt:
            print()
            return None
        if (check_valid_input(question, answer) and
            check_valid_answer_length(question, answer)):
            return answer

def InvalidArgError(ValueError):
    pass

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print()

def usage():
    print("""
py questions.py -[s|v]
    -s : shuffle question set
    -v : verbose results
    -a : answers shown on incorrectly answered questions
    -f : file path to question set"""[1:]
    )

if __name__ == "__main__":
    # system args parsing:
    if sys.argv:
        for arg in sys.argv:
            if arg == '-s':
                q_sort = True
            elif arg == '-a':
                show_answer = True
            elif arg == '-v':
                verbose = True

    # load the question set
    with open(file_import, "r") as f:
        data = json.load(f)
    # convert them to question objects
    questions = [Question(d) for d in data]
    # randomize order of questions
    if q_sort:
        random.shuffle(questions)
    for i, q in enumerate(questions):
        clear_screen()
        ask_question(q, i+1)
        answer = handle_input(q)
        if not answer:
            break
        q.answered = True
        if check_correct_answer(q, answer):
            q.correct = True
        if show_answer:
            if q.correct:
                print(f"{x_indent}Correct")
            else:
                print(f"{x_indent}Incorrect: {', '.join(chr(97+a) for a in q.answer)}")
            try:
                input(f"{x_indent}Press any key to continue...")
            except KeyboardInterrupt:
                break
    print_results(questions)

