import numpy
from random import randint
from datetime import datetime
from functools import wraps
import sys
import interpreter as io

EXIT_REQUEST = ["exit", "quit", "end"]
HELP_REQUEST = "help"

LEVELS = {0: {"start_num": 1,
              "end_num":   10,
              "numbers":   2},

          1: {"start_num": 1,
              "end_num":   20,
              "numbers":   2},

          2: {"start_num": 10,
              "end_num":   99,
              "numbers":   2},

          3: {"start_num": 10,
              "end_num":   299,
              "numbers":   2},
          }


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = f(*args, **kwargs)
        time_diff = datetime.now() - start
        return result, time_diff.seconds
    return wrapper


class Question(object):
    def __init__(self, question_type="Multiple", level=0):
        parameters = LEVELS[level]
        self.numbers = Question.generate_numbers(**parameters)
        self.type = question_type
        self.correct_answer = None
        self.user_answer = None
        self.time = 0

        if question_type == "Multiple":
            self.correct_answer = numpy.prod(self.numbers)


    @staticmethod
    def generate_numbers(start_num=1, end_num=20, numbers=2):
        return [randint(start_num, end_num) for _ in range(numbers)]


    def ask(self):
        if self.type == "Multiple":
            io.send("question multiple", *self.numbers)
        self.user_answer, self.time = Question.get_answer()


    @property
    def check(self):
        return self.user_answer == self.correct_answer


    @staticmethod
    @timing
    def get_answer():
        user_input = io.receive("answer")
        if user_input.isdigit():
            return int(user_input)
        elif user_input in EXIT_REQUEST:
            Game.exit_game()
        Game.help()
        return Question.get_answer()


class Game(object):
    def __init__(self, name, start_level=0):
        self.streak = 0
        self.name = name
        self.level = start_level
        self.question = None

        io.send("welcome", name=self.name)


    def run(self):
        self.ask_question()

        if self.question.check:
            io.send("success", end=' ')
            self.streak += 1
        else:
            correct_answer = self.question.correct_answer
            io.send("failure", correct_answer)
            self.streak = 0

        if self.streak > 3:
            io.send("streak", streak=self.streak)

        time = self.question.time
        io.send("time", time=time)

        print()
        self.run()


    @staticmethod
    def exit_game():
        io.send("quit")
        sys.exit()


    @staticmethod
    def help():
        io.send("help")


    def ask_question(self):
        self.question = Question("Multiple", self.level)
        self.question.ask()


def main():
    name = "Kfir"
    new_game = Game(name)
    new_game.run()


if __name__ == "__main__":
    main()