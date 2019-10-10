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
Then run the reader.py file
```
py reader.py [args]
```
Running reader.py will create questions.json file which can be read by questions.py
```
py questions.py [args]
```

TODO:
```
specify filepath/inputs
handle input arguments into reader and question python files
```
