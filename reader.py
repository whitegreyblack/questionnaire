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

question_start_pattern = "^(\d*\.)(.*)$" 
question_start = re.compile(question_start_pattern)
question_continue_pattern = "^(\t|   )(.*)$"
question_continue = re.compile(question_continue_pattern)
codeblock_pattern = "^\\\"{3}?.*$"
codeblock = re.compile(codeblock_pattern)
codeline_pattern = "^(\t|   )?((\d*\.|\.{2})?.*)$" 
codeline = re.compile(codeline_pattern)
answers_pattern = "^(\t|    )[a-e]\.(.*)$"
answers = re.compile(answers_pattern)
answer_pattern = "^(A\..*)\((.*)\).*$"
answer = re.compile(answer_pattern)
width, _ = os.get_terminal_size()

def debug(*args):
    if __debug__:
        print(*args)

def dump(question):
    return json.dumps(question, indent=2)

def evaluate_error(question, pattern):
    if question.answers and pattern is not answer_pattern:
        return "Final answer string (A. ([a-e]+))"
    else:
        return "Error not specified"

def print_reader_error(question, question_number, line_number, line, in_code, code_added, pattern):
    expected = evaluate_error(question, pattern)
    print(f"""
  Question {question_number + 1}, line {line_number + 1}
    Got: {repr(line if len(line) < 72 else line[:69] + '...')}
    Expected: {expected}
  inside code block: {in_code}
  code block added: {code_added}
Reader Error: """[1:])

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
    last_matched_pattern = None
    
    with open(file_name, "r") as f:
        lines = f.readlines()

    for l, line in enumerate(lines):
        # disregard comments or empty lines
        if line.startswith("--") or line == "\n":
            continue

        # beginning question statement
        matched = question_start.match(line)
        if matched:
            last_matched_pattern = question_start.pattern
            if question.empty and not code_block_start:
                question.before.append(matched.groups()[1].strip())
                continue

        # possible answers statement
        matched = answers.match(line)
        if matched and not question.before:
            last_matched_pattern = answers.pattern
            question.answers.append(Answer(text=matched.groups()[1].strip()))
            continue

        # possible code block
        matched = codeblock.match(line)
        if matched:
            last_matched_pattern = codeblock.pattern
            if code_block_start:
                code_block_start = False
                code_block_added = True
            else:
                code_block_start = True
            continue

        # possible code line - only valid if code_block_start is on
        matched = codeline.match(line)
        if matched:
            last_matched_pattern = codeline.pattern
            if code_block_start:
                question.code.append(matched.groups()[1])
                continue
        
        # continuing question statement - set last so any lines that don't 
        # match are sent here
        matched = question_continue.match(line)
        if matched:
            last_matched_pattern = question_continue.pattern
            container = question.before if not code_block_added else question.after
            container.append(matched.group().strip())
            continue
        
        # correct answer statement - reached end of question. serialize it
        matched = answer.match(line)
        if matched:
            last_matched_pattern = answer.pattern
            # somehow code block was entered but not correctly escaped
            if code_block_start:
                raise ValueError(f"{l+1}: Code block not correctly ended")
            question.set_correct_answers(matched.groups()[1].strip())

            # serialize question
            serialized_question = question.serialize()
            questions.append(serialized_question)
            question.clear()
            code_block_start = False
            code_block_added = False
            continue

        print_reader_error(
            question, 
            len(questions), 
            l, 
            line, 
            code_block_start, 
            code_block_added, 
            last_matched_pattern)
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
