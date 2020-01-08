# config.py

"""Holds variables used in quizzer and reader scripts"""


# data files
data_path = "data"

# file names
file_name_text = f"{data_path}/questions.txt"
file_name_json = f"{data_path}/questions.json"

# terminal properties
width_min = 100
height_min = 24

# quizzer variables
verbose = False
randomize_answers = False
randomize_questions = False
show_answer = [False, False] # on incorrect, on correct

# lexer variables
lex_test_file_name_in = f"{data_path}/question.txt"
lex_test_file_name_out = f"{data_path}/tokens.txt"

# parser variables
parse_test_file_name_in = f"{data_path}/tokens.txt"
parse_test_file_name_out = f"{data_path}/ast.txt"

# reader variables
reader_test_file_name_in = f"{data_path}/question.txt"
reader_test_file_name_out = f"{data_path}/questions.json"

