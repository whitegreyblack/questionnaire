# reader.py

"""Read question set file and convert into json"""

import json
import os
import re
import sys
from dataclasses import dataclass

import click
from config import file_name_json, file_name_text
from model import AnswerBuilder as Answer
from model import QuestionBuilder as Question


question_start = re.compile("^(\d*\.)(.*)$")
question_continue = re.compile("^(\t|   )(.*)$")
codeblock = re.compile("^\\\"{3}?.*$")
codeline = re.compile("^(\t|   )?((\d*\.|\.{2})?.*)$")
answers = re.compile("^(\t|    )[a-e]\.(.*)$")
answer = re.compile("^(A\..*)\((.*)\).*$")
width, _ = os.get_terminal_size()

def debug(*args):
    if __debug__:
        print(*args)

def dump(question):
    return json.dumps(question, indent=2)

def print_reader_error(question_number, line_number, line, in_code, code_added):
    print(f"""
Reader error: Question {question_number + 1} Line {line_number + 1}: {repr(line)}
    inside code block: {in_code}
    code block added: {code_added}"""[1:])

def create_json_file(questions, file_name):
    if not questions:
        return
    with open(file_name, "w") as f:
        json.dump(questions, f, indent=2)
    print(f"Created {len(questions)} questions in {file_name}")

def parse_text(file_name):
    code_block_start = False
    code_block_added = False
    questions = []
    question = Question()
    
    with open(file_name, "r") as f:
        lines = f.readlines()

    for l, line in enumerate(lines):
        # disregard comments or empty lines
        if line.startswith("--") or line == "\n":
            continue

        # beginning question statement
        qs = question_start.match(line)
        if qs and not code_block_start:
            question.before.append(qs.groups()[1].strip())
            continue

        # possible answers statement
        a = answers.match(line)
        if a:
            question.answers.append(Answer(text=a.groups()[1].strip()))
            continue

        # possible code block
        cb = codeblock.match(line)
        if cb:
            if code_block_start:
                code_block_start = False
                code_block_added = True
            else:
                code_block_start = True
            continue

        # possible code line - only valid if code_block_start is on
        cl = codeline.match(line)
        if cl and code_block_start:
            question.code.append(cl.groups()[1])
            continue
        
        # continuing question statement - set last so any lines that don't 
        # match are sent here
        qc = question_continue.match(line)
        if qc:
            container = question.before if not code_block_added else question.after
            container.append(qc.group().strip())
            continue
        
        # correct answer statement - reached end of question. serialize it
        a = answer.match(line)
        if a:
            # somehow code block was entered but not correctly escaped
            if code_block_start:
                raise ValueError(f"{l+1}: Code block not correctly ended")
            question.set_correct_answers(a.groups()[1].strip())

            # serialize question
            serialized_question = question.serialize()
            questions.append(serialized_question)
            question.clear()
            code_block_start = False
            code_block_added = False
            continue
        print_reader_error(len(questions), l, line, code_block_start, code_block_added)
        break
    return questions

@click.command()
@click.argument('file_name_in', default=file_name_text)
@click.argument('file_name_out', default=file_name_json)
def main(file_name_in, file_name_out):
    questions = parse_text(file_name_in)
    create_json_file(questions, file_name=file_name_out)

if __name__ == "__main__":
	main()
