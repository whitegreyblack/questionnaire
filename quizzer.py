# questions.py

"""Questionnaire application"""
   
import json
import os
import pprint
import random
import sys
import textwrap

from config import file_name_json, width_min, height_min
from dataclasses import dataclass
from model import Question

# input argument flags with defaults and variables
numbers = []
verbose = False
show_answer = False
save_results = False
print_results = True
shuffle_answers = False
shuffle_questions = False

# ui constants
width, height = os.get_terminal_size()
y_offset = ((height - height_min) // 2) if height > height_min else 0
x_offset = ((width - width_min) // 2) if width > width_min else 0
x_indent = " " * x_offset
code_indent = " " * 4
indent = "  "

def results_to_file(text) -> None:
    """saves results to a file named 'attempt_x'"""
    attempts = get_next_attempt_value_from_directory_names()
    filename = f"attempt_{attempts}.txt"
    with open(filename, "w") as f:
        f.write(text)
    print(f"Written results to: {filename}")

def results_to_term(text) -> None:
    clear_screen()
    print(text)

def get_next_attempt_value_from_directory_names() -> int:
    """Returns next integer value to use in filename when saving results"""
    for _, _, files in os.walk("."):
        current = 1 # default attempt name value begins at 1
        for filename in files:
            if filename.startswith("attempt"):
                # removes "attempt_" and ".txt"
                attempt = int(filename.split("_")[1].split(".")[0])
                if attempt > current:
                    current = attempt + 1
        return current

def output_results(questions):
    """Handles output to either terminal or file"""
    global print_results, save_results, verbose

    # nothing to output
    if all(not q.answered for q in questions):
        return

    # somehow no output options were set. this should not happen, set print on
    if not print_results and not save_results:
        print_results = True

    # calculate results
    correct = sum(int(q.answered and q.correct) for q in questions)
    answered = sum(int(q.answered) for q in questions)
    total = len(questions)
    lines = []

    # verbose currently only adds the question id that was incorrectly answered
    # TODO: add coloring (maybe from colorama)
    #     : add full question and answers text
    lines.append(f"Results:")
    lines.append(f"  {correct}/{answered} questions ({correct/answered * 100:.2f}%)")
    lines.append(f"  {correct}/{total} questions ({correct/total * 100:.2f}%)")

    # output more information if flag is set
    if verbose:
        lines.append("Incorrect:")
        lines.append('\n'.join(
            str(q.question_id)
                for q in questions 
                    if q.answered and not q.correct)
            )

    text = "\n".join(lines)

    # determine if results are saved && printed, just saved or just printed
    # something will always print regardless of to term or to file
    if save_results and print_results:
        results_to_file(text)
        results_to_term(text)
    elif save_results:
        results_to_file(text)
    else:
        results_to_term(text)

def ask_question(question, question_id):
    qid = question.question_id if not shuffle_questions else question_id
    # append the question text
    text = [
        f"{x_indent}{str(qid) + '.' if i < 1 else indent} {s}"
            for i, s in enumerate(
                textwrap.wrap(question.question, 80 - len(indent) - 2)
            )
        ]
    text.append('')
    
    # if any code blocks are included in the question
    if question.code:
        for line in question.code:
            text += [
                f"{x_indent}{code_indent} {s}"
                    for s in textwrap.wrap(line, width - len(x_indent) - len(code_indent))
                ]
        text.append('')
    
    # any text after the code block is now added
    if question.additional:
        text += [
            f"{x_indent}{indent} {s}"
                for i, s in enumerate(
                    textwrap.wrap(question.additional, 80 - len(indent) - 2)
                )
            ]
        text.append('')

    # TODO: randomize answers within a question
    # save the full answer text to find index later after randomization
    # answer = question.answers[question.answer]
    # random.shuffle(question.answers)
    # question.answer = question.answers.indexof(answer)
    
    # append the answers text
    for i, answer in enumerate(question.answers):
        for j, s in enumerate(textwrap.wrap(answer, 80 - len(indent * 2) - 4)):
            answer_char = chr(i + 97) + '.' if j < 1 else '  '
            text.append(f"{x_indent}{indent * 2}{answer_char} {s}")
        text.append('')
    # output question and answer format
    print('\n'.join(' ' for _ in range(y_offset)), '\n'.join(text), '')

def check_valid_input(question, answer):
    # creates a set ranging from a->d|e depending on number of possible answers
    answers = ''.join(chr(97+i) for i in range(len(question.answers)))
    # checks if all input characters are in the answer set
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

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')
    print()

def usage():
    print("""
py questions.py -[afosvS]
    -s : shuffle question set
    -o : shuffle answer set per question
    -S : save results to file <attempt_#>.txt
    -v : verbose results
    -a : answers shown on incorrectly answered questions
    -f : file path to question set"""[1:]
    )

def handle_args(args):
    """parse input arguments"""
    global shuffle_questions, shuffle_answers, show_answer, verbose
    global save_results, numbers
    args = {'file_name_json': file_name_json }
    if sys.argv:
        for arg in sys.argv[1:]:
            if arg == '-h':
                usage()
                exit(0)
            elif arg.startswith('--file='):
                # defaults to file_name_json if not set
                args['file_name_json'] = arg.split('=')[1]
            elif arg == '-s':
                shuffle_questions = True
            elif arg == '-o':
                shuffle_answers = True
            elif arg == '-a':
                show_answer = True
            elif arg == '-v':
                verbose = True
            elif arg == '-S':
                save_results = True
                print(save_results)
            elif arg.startswith('--questions='):
                # TODO: select questions from a set of numbers
                # and use it to test
                _, number = arg.split('=')
                numbers = number.split(' ')
            else:
                print(f"{arg} does not match any flags")
    return args

def main():
    # global variables set before parsing questions    
    args = handle_args(sys.argv)

    # load the question set
    with open(args['file_name_json'], "r") as f:
        data = json.load(f)
    
    # convert them to question objects
    questions = [Question(d, shuffle=shuffle_answers) for d in data]
    
    # randomize order of questions
    if shuffle_questions:
        random.shuffle(questions)
    
    # render each question and wait for input from user
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
                input(f"{x_indent}Press <enter> to continue...")
            except KeyboardInterrupt:
                break

    output_results(questions)

if __name__ == "__main__":
	main()
