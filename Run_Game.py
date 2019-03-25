import numpy
from random import randint
from datetime import datetime
from functools import wraps
import sys
import terminal as io
import log

EXIT_REQUEST = ["exit", "quit", "end"]
HELP_REQUEST = "help"

LEVELS = {1: {"start_num": 1, "end_num":   10, "numbers":   2},
          2: {"start_num": 1, "end_num":   20, "numbers":   2},
          3: {"start_num": 1, "end_num":   10, "numbers":   3},
          4: {"start_num": 1, "end_num":   99, "numbers":   2},
          5: {"start_num": 1, "end_num":   29, "numbers":   3},
          6: {"start_num": 1, "end_num":   79, "numbers":   3},
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
    def __init__(self, question_type="Multiple", level=1):
        parameters = LEVELS[level]
        self.numbers = Question.generate_numbers(**parameters)
        self.type = question_type
        self.correct_answer = None
        self.user_answer = None
        self.points = 0
        self.time = 0
        self.level = level

        if question_type == "Multiple":
            operator = '*'
            self.question = operator.join(map(str, self.numbers))
            self.correct_answer = numpy.prod(self.numbers)


    @staticmethod
    def generate_numbers(start_num=1, end_num=20, numbers=2):
        return [randint(start_num, end_num) for _ in range(numbers)]


    def ask(self):
        io.send("question", question=self.question, level=self.level)

        answered = False
        while not answered:
            self.user_answer, self.time = Question.get_answer()
            if self.user_answer is None:
                Game.help()
            else:
                answered = True

        self.calculate_points()


    def calculate_points(self):
        if self.check:
            self.points += int(self.level * 100 / self.time)
        else:
            self.points -= 100


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
            return user_input
        return None


class Game(object):
    def __init__(self, name, start_level=1):
        self.streak = 0
        self.max_streak = 0
        self.total_points = 0
        self.name = name
        self.level = start_level
        self.question = None

        io.send("welcome", name=self.name)


    def run(self):
        if self.streak % 5 == 0 and self.streak and self.level < max(LEVELS.keys()):
            self.level += 1
            io.send("level up", level=self.level)

        self.ask_question()
        self.try_exit()

        self.total_points += self.question.points
        self.log()

        if self.question.check:
            io.send("success")
            self.streak += 1
        else:
            io.send("failure", self.question.correct_answer)
            self.streak = 0
            self.level = max(min(LEVELS.keys()), self.level - 1)

        self.max_streak = max(self.max_streak, self.streak)
        if self.streak > 3:
            io.send("streak", streak=self.streak)
        io.send("points", points=self.total_points, end=' ')
        io.send("time", time=self.question.time)
        io.send("question end")

        self.run()


    def log(self):
        data = (self.name, self.level, self.total_points, self.streak, self.question.question, self.question.user_answer, self.question.correct_answer, self.question.check)
        #data = tuple(map(str, data))
        with  log.DatabaseConnection('GameDB') as db:
            db.append(data)


    def try_exit(self):
        if self.question.user_answer in EXIT_REQUEST:
            io.send("quit", streak=self.max_streak, points=self.total_points)
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