# reader.py

"""Read question set file and convert into json"""

import json
import sys
import os
import re


file_path = "./questions.txt"

question_start = re.compile("^(\d*\.) (.*).*$")
question_continue = re.compile("^(\t|   )(.*).*$")
answers = re.compile("^(\t|    )[a-e]\.(.*).*$")
answer = re.compile("^(A\..*)\((.*)\).*$")
width, _ = os.get_terminal_size()

def output(question):
    print(json.dumps(question, indent=2))

def create_json(questions, filename="questions.json"):
    with open(filename, "w") as f:
        json.dump(questions, f, indent=2)

def parse_text(file_path):
    questions, question, answer_set = [], [], []
    with open(file_path, "r") as f:
        lines = f.readlines()
    for l, line in enumerate(lines):
        if line.startswith("--") or line == "\n":
            continue
        qs = question_start.match(line)
        if qs:
            question.append(qs.groups()[1].strip())
            continue
        a = answers.match(line)
        if a:
            answer_set.append(a.groups()[1].strip())
            continue
        qc = question_continue.match(line)
        if qc:
            question.append(qc.group().strip())
            continue
        a = answer.match(line)
        if a:
            value = a.groups()[1].strip()
            values = [ord(v.strip())-97 for v in value.split(',')]
            questions.append({
                'question': ' '.join(question),
                'answers': answer_set,
                'answer': values
            })
            question, answer_set = [], []
            continue
        raise ValueError(f"{l+1}: {repr(line)}")
    return questions

if __name__ == "__main__":
    # sys.argv will handle input args
    questions = parse_text(file_path)
    create_json(questions)
    print(f"Created {len(questions)} questions and saved in questions.json")

