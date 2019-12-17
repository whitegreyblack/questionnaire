# questionnaire
Small script to run a simple questionnaire program

First need a question set where questions are formatted like:
```
# questions.txt
1. An example question.
    a. Answer 1
    b. Answer 2
    ...
    n. Answer n
A. (a, c, n) # whatever answers are correct. Can be a single answer or multiple
```
Now handles questions with a code block included in the question:
```
# questions.txt
2. An example question with a code block:
-- two dashed lines are skipped in reader.py
"""
1. class foo () {
2.     private method() {}
3. }
-- or 
   class bar () {
   	public method() {}
   }
"""
   Additional information can be optionally added after the code block
    a. Answer 1
    ...
    n. Answer n
A. (a, c, n)
```
Then run the reader.py file with the input questions file and an optional output file name
```
py reader.py [file_name_in] [file_name_out]
```
Running reader.py will create a json file containing a list of parsed questions which can be read by quizzer.py
```
py quizzer.py [args] [--file=filename]
```
