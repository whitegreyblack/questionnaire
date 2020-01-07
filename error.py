# error.py

class Error(Exception):
    def __init__(self, error_code=None, token=None, message=None):
        self.error_code = error_code
        self.token = token
        self.message = message

class LexerError(Error):
    pass

class ParserError(Error):
    pass
