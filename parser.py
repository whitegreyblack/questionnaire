# parser.py
import click

from config import file_name_text
from error import ParserError
from lexer import (COMMA, COMMENT, ENDMARKER, LETTER_LOWER, LETTER_UPPER,
                   LPAREN, NUMBER, PERIOD, RPAREN, SYMBOL, SYMBOLS, TAB, WORD,
                   read_from_file, tokenize)

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
        return ", ".join(answers)

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

def consume(source, tokens, token_type):
    token = tokens.pop(0)
    if token.type == token_type:
        return token
    else:
        error(f"""
  {__file__}, {source}()
    Got: {token.type} ({repr(token.value)})
        
ParserError: unexepected token. Expected: {token_type} token"""[1:])

def question_id(tokens):
    number = consume('question_id', tokens, NUMBER)
    symbol = consume('question_id', tokens, PERIOD)
    return QuestionId(number, symbol)

def is_period(token):
    return token.type == PERIOD and token.value == '.'

def is_symbol(token):
    return token.type in (SYMBOL, PERIOD, LPAREN, RPAREN, COMMA)

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
    tabchr = consume('choice_id', tokens, TAB)
    letter = consume('choice_id', tokens, LETTER_LOWER)
    symbol = consume('choice_id', tokens, PERIOD)
    return QuestionId(letter, symbol)

def question_choices(tokens):
    choices = []
    while True:
        cid = choice_id(tokens)
        sentence = sentence_statement(tokens)
        choices.append(ChoiceStatement(cid, sentence))
        if tokens[0].type != TAB:
            break
    return choices

def question_answer(tokens):
    answers = []
    letter = consume('question_answer', tokens, LETTER_UPPER)
    symbol = consume('question_answer', tokens, PERIOD)
    lparen = consume('question_answer', tokens, LPAREN)
    while True:
        letter = consume('question_answer', tokens, LETTER_LOWER)
        answers.append(letter)
        if tokens[0].type == COMMA:
            symbol = consume('question_answer', tokens, COMMA)
            continue
        if tokens[0].type == RPAREN:
            rparen = consume('question_answer', tokens, RPAREN)
            break
    return AnswerStatement(answers)

def question_block(tokens):
    qid = question_id(tokens)
    statement = question_statement_pre(tokens)
    choices = question_choices(tokens)
    answer = question_answer(tokens)
    return QuestionBlock(qid, statement, choices, answer)

def questions(tokens):
    blocks = []
    while tokens:
        block = question_block(tokens)
        blocks.append(block)
        break
    return blocks

def parse(tokens):
    blocks = questions(tokens)
    for b in blocks:
        print(b.preview())
    if tokens[0].type != ENDMARKER:
        print(tokens[0:4], len(tokens))
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
