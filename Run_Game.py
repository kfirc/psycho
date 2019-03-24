import numpy
from random import randint
from datetime import datetime
from functools import wraps
import sys
import terminal as io

EXIT_REQUEST = ["exit", "quit", "end"]
HELP_REQUEST = "help"

LEVELS = {1: {"start_num": 1,
              "end_num":   10,
              "numbers":   2},

          2: {"start_num": 1,
              "end_num":   20,
              "numbers":   2},

          3: {"start_num": 1,
              "end_num":   10,
              "numbers":   3},

          4: {"start_num": 1,
              "end_num":   99,
              "numbers":   2},

          5: {"start_num": 1,
              "end_num":   29,
              "numbers":   3},

          6: {"start_num": 1,
              "end_num":   79,
              "numbers":   3},
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
        self.time = 0
        self.level = level

        if question_type == "Multiple":
            self.correct_answer = numpy.prod(self.numbers)


    @staticmethod
    def generate_numbers(start_num=1, end_num=20, numbers=2):
        return [randint(start_num, end_num) for _ in range(numbers)]


    def ask(self):
        if self.type == "Multiple":
            operator = '*'
        question = operator.join(map(str, self.numbers))
        io.send("question", question=question, level=self.level)
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
            return user_input
        Game.help()
        return Question.get_answer()


class Game(object):
    def __init__(self, name, start_level=1):
        self.streak = 0
        self.max_streak = 0
        self.points = 0
        self.name = name
        self.level = start_level
        self.question = None

        io.send("welcome", name=self.name)


    def calculate_points(self):
        if self.question.check:
            self.points += int(self.level * 100 / self.question.time)
        else:
            self.points -= 100

        return self.points


    def run(self):
        if self.streak % 5 == 0 and self.streak and self.level < max(LEVELS.keys()):
            self.level += 1
            io.send("level up", level=self.level)

        self.ask_question()

        if self.question.user_answer in EXIT_REQUEST:
            self.exit_game()
        else:
            points = self.calculate_points()
            time = self.question.time
            correct_answer = self.question.correct_answer

            if self.question.check:
                io.send("success")
                self.streak += 1
            else:
                io.send("failure", correct_answer)
                self.streak = 0
                self.level = max(min(LEVELS.keys()), self.level - 1)

            if self.streak > 3:
                io.send("streak", streak=self.streak)
            io.send("points", points=points, end=' ')
            io.send("time", time=time)
            io.send("question end")

            self.max_streak = max(self.max_streak, self.streak)
            self.run()


    def exit_game(self):
        io.send("quit", streak=self.max_streak, points=self.points)
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