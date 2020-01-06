# parser.py

import Enum, auto

class TokenList(Enum):
    WHITESPACE = auto() # [ ]*
    NEWLINE = auto() # \n
    QUESTION_ID = auto() # [1-9]*[1-9]+
    WORD = auto() # [a-zA-Z]
    NUMBER = auto() # [0-9]+
    SYMBOL = auto() # :?_;.
    ANSWER_CHOICE = auto() # [a-e].
    ANSWER = auto() # A.
    ANSWER_SET = auto() # \(([a-e],)*[a-e]+)

if __name__ == "__main__":
    ...

