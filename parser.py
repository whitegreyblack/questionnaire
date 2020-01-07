# parser.py
import click

from config import file_name_text
from error import ParserError
from lexer import (LETTER_LOWER, LETTER_UPPER, NUMBER, SYMBOL, SYMBOLS, TAB,
                   WORD, read_from_file, tokenize, ENDMARKER)

QUESTION_ID = 'question_id' # [1-9]*[1-9]+
SENTENCE = 'sentence'
ANSWER_CHOICE = 'answer_choice' # [a-e].
ANSWER = 'answer' # A.
ANSWER_SET = 'answer_set' # \(([a-e],)*[a-e]+)

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
    def __init__(self, question_id, statement, choices):
        self.qid = question_id
        self.stmt = statement
        self.choices = choices
    # def __init__(self, qid, statement, choices, answer, code=None, after=None):
    #     self.qid = qid
    #     self.statement = statement
    #     self.choices = choices
    #     self.answer = answer
    #     self.code = code
    #     self.after = after

    def __repr__(self):
        return f"{self.qid} number of choices: {len(self.choices)}"

# class AnswerStatement:
#     ...

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

# class AnswersBlock:
#     ...

def error(message):
    e = ParserError(message=message)
    print(e.message)
    exit(1)

def check_if_number(token):
    if token.type is not NUMBER:
        error(f"Expected number token for question id. Got: {token}")

def check_if_tab(token):
    if token.type is not TAB:
        error(message=f"Expected tab token for question choice statement. Got: {token}")

def check_if_period(token):
    if token.type is not SYMBOL or (token.type is SYMBOL and token.value != '.'):
        error(f"Expected symbol token for question id. Got: {token}")

def check_if_letter(token):
    if not is_letter(token):
        error(f"Expected letter token for choice id. Got: {token}")

def question_id(tokens):
    number = tokens.pop(0)
    check_if_number(number)
    symbol = tokens.pop(0)
    check_if_period(symbol)
    return QuestionId(number, symbol)

def is_period(token):
    return token.type == SYMBOL and token.value == '.'

def is_symbol(token):
    return token.type == SYMBOL

def is_letter(token):
    return token.type == LETTER_UPPER or token.type == LETTER_LOWER

def is_word(token):
    return token.type == WORD or is_letter(token)

def is_capitalized_word(token):
    return token.type == WORD and str.isupper(token.value[0])

def is_lowercase_word(token):
    return token.type == WORD and not str.isupper(token.value[0])

def sentence_statement(tokens):
    token = tokens.pop(0)
    sentence = []
    while token:
        if not is_symbol(token) and not is_word(token):
            break
        sentence.append(token.value)
        word_to_word = is_word(token) and is_word(tokens[0])
        symbol_to_word = not is_period(token) and is_lowercase_word(tokens[0])
        if word_to_word or symbol_to_word:
            sentence.append(' ')
        token = tokens.pop(0)
    tokens.insert(0, token)
    return "".join(sentence)

def question_statement_pre(tokens):
    return QuestionStatement(sentence_statement(tokens))

def choice_id(tokens):
    letter = tokens.pop(0)
    check_if_letter(letter)
    symbol = tokens.pop(0)
    check_if_period(symbol)
    return QuestionId(letter, symbol)

def question_choices(tokens):
    choices = []
    while True:
        tab = tokens.pop(0)
        check_if_tab(tab)
        cid = choice_id(tokens)
        sentence = sentence_statement(tokens)
        choices.append(ChoiceStatement(cid, sentence))
        if tokens[0].type != TAB:
            break
    return choices

def question(tokens):
    qid = question_id(tokens)
    statement = question_statement_pre(tokens)
    choices = question_choices(tokens)
    return QuestionBlock(qid, statement, choices)

def questions(tokens):
    blocks = []
    while tokens:
        block = question(tokens)
        blocks.append(block)
        break
    return blocks

def parse(tokens):
    blocks = questions(tokens)
    print(blocks)
    if tokens[0].type != ENDMARKER:
        print(tokens)
        error("Not all tokens consumed")
    return blocks

@click.command()
@click.argument('file_name_in', default=file_name_text)
def main(file_name_in):
    text = read_from_file(file_name_in)
    tokens = tokenize(text)
    blocks = parse(tokens)

if __name__ == "__main__":
	main()
