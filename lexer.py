# lexer.py

import click

from config import file_name_text
from error import LexerError

offset = [65, 97]
ALPHABET = "".join(chr(offset[j] + i) for i in range(26) for j in range(2))
NUMERIC = "".join(str(i) for i in range(10))
SYMBOLS = "\\-':?_;.,<>/()"
WORD = 'word' # [a-zA-Z]
LETTER_UPPER = 'letter upper'
LETTER_LOWER = 'letter lower'
WHITESPACE = 'whitespace' # [ ]*
NEWLINE = 'newline' # \n
TAB = 'tab' # '\t'
NUMBER = 'number' # [0-9]+
SYMBOL = 'symbol' # \-':?_;.,<>/
COMMENT = 'comment' # --
ENDMARKER = 'endmarker' # '' (empty string)

class Token:
    def __init__(self, token_type, value):
        self.type = token_type
        self.value = value
    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

def read_from_file(file_name):
    with open(file_name, "r") as f:
        lines = f.read()
    return lines

def skip_until_nondigit(text, position):
    while True:
        position = advance(text, position)
        if position < 0 or (position >= 0 and not text[position] in NUMERIC):
            return position

def skip_until_newline(text, position):
    while True:
        position = advance(text, position)
        if position < 0 or (position >= 0 and text[position] == '\n'):
            return position

def skip_until_nonspace(text, position):
    while True:
        position = advance(text, position)
        if position < 0 or (position >= 0 and not text[position] == ' '):
            return position

def skip_until_nonalpha(text, position):
    while True:
        position = advance(text, position)
        if position < 0 or (position >= 0 and not text[position] in ALPHABET):
            return position

def advance(text, position):
    if position + 1 > len(text) - 1:
        return -1
    return position + 1

def prev_char(text, position):
    if position < 0:
        return None
    return text[position - 1]

def next_char(text, position):
    if position + 1 > len(text) - 1:
        return None
    return text[position + 1]

def tokenize(text):
    position = 0
    tokens = []

    while True:
        if position < 0:
            break
        char = text[position]
    
        # whitespace
        if char == ' ':
            position = skip_until_nonspace(text, position)
            continue
    
        # comments
        if char == '-' and next_char(text, position) == '-':
            start = position
            position = skip_until_newline(text, position)      
            # tokens.append(Token(COMMENT, text[start:position]))
            continue
    
        # tabs
        if char == '\t':
            tokens.append(Token(TAB, char))
            position = advance(text, position)
            continue

        # symbols
        if char in SYMBOLS:
            tokens.append(Token(SYMBOL, char))
            position = advance(text, position)
            continue

        # newlines
        if char == '\n':
            # tokens.append(Token(NEWLINE, char))
            position = advance(text, position)
            continue

        # numbers
        if char.isdigit():
            start = position
            position = skip_until_nondigit(text, position)
            tokens.append(Token(NUMBER, text[start:position]))
            continue

        # words
        if char in ALPHABET:
            start = position
            position = skip_until_nonalpha(text, position)
            characters = text[start:position]
            if len(characters) > 1:
                token_type = WORD
            elif str.isupper(characters):
                token_type = LETTER_UPPER
            else:
                token_type = LETTER_LOWER
            tokens.append(Token(token_type, characters))
            continue

        e = LexerError(message=f"Invalid character: {char}")
        print(e.message)
        exit(1)

    tokens.append(Token(ENDMARKER, ''))
    return tokens

@click.command()
@click.argument('file_name_in', default=file_name_text)
def main(file_name_in):
    text = read_from_file(file_name_in)
    tokens = tokenize(text)
    for t in tokens:
        print(t)

if __name__ == "__main__":
	main()
