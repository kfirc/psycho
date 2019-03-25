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
    def __init__(self, question_type, current_streak, initial_level=1):
        parameters = LEVELS[initial_level]
        self.numbers = Question.generate_numbers(**parameters)
        self.type = question_type
        self.correct_answer = None
        self.user_answer = None
        self.points = 0
        self.time = 0
        self.current_streak = current_streak
        self.level = initial_level

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
        if self.correct:
            self.points += int(self.level * 100 / self.time)
        else:
            self.points -= 100


    @property
    def correct(self):
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


    def log(self):
        question_data = (self.level, self.points, self.current_streak, self.question, self.user_answer, self.correct_answer, self.correct)
        with log.DatabaseConnection('questions') as db:
            db.append(question_data)


class Game(object):
    def __init__(self, name, start_level=1):
        self.current_streak = 0
        self.max_streak = 0
        self.total_points = 0
        self.name = name
        self.level = start_level
        self.question = None

        io.send("welcome", name=self.name)


    def run(self):
        if self.current_streak % 5 == 0 and self.current_streak and self.level < max(LEVELS.keys()):
            self.level += 1
            io.send("level up", level=self.level)

        self.ask_question()
        self.try_exit()
        self.question.log()
        self.total_points += self.question.points

        if self.question.correct:
            io.send("success")
            self.current_streak += 1
        else:
            io.send("failure", self.question.correct_answer)
            self.current_streak = 0
            self.level = max(min(LEVELS.keys()), self.level - 1)

        self.max_streak = max(self.max_streak, self.current_streak)
        if self.current_streak > 3:
            io.send("streak", streak=self.current_streak)
        io.send("points", points=self.total_points, end=' ')
        io.send("time", time=self.question.time)
        io.send("question end")

        self.run()


    def log(self):
        game_data = (self.name, self.level, self.total_points, self.max_streak)
        with log.DatabaseConnection('games') as db:
            db.append(game_data)


    def try_exit(self):
        if self.question.user_answer in EXIT_REQUEST:
            io.send("quit", streak=self.max_streak, points=self.total_points)
            self.log()
            sys.exit()


    @staticmethod
    def help():
        io.send("help")


    def ask_question(self):
        question_type = "Multiple"
        self.question = Question(question_type, self.current_streak, self.level)
        self.question.ask()


def main():
    name = "Kfir"
    new_game = Game(name)
    new_game.run()


if __name__ == "__main__":
    main()