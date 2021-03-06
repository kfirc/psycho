import numpy
from random import randint
from datetime import datetime
from functools import wraps
import sys
import terminal as io
import log


EXIT_REQUEST = ["exit", "quit", "end"]
HELP_REQUEST = "help"
NUMBER_OF_LEVELS = 6


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = f(*args, **kwargs)
        time_diff = datetime.now() - start
        return result, time_diff.seconds
    return wrapper



class Level(object):
    def __init__(self, level):
        with log.DatabaseConnection('levels') as table:
            df = table.read()

        self.level = level
        parameters = df.loc[[level]].to_dict(orient='records')[0]
        self.start_num = parameters["start_num"]
        self.end_num = parameters["end_num"]
        self.numbers = parameters["numbers"]
        self.time = parameters["time"]


    def generate_numbers(self):
        return [randint(self.start_num, self.end_num) for _ in range(self.numbers)]


class Question(object):
    def __init__(self, question_type, current_streak, level):
        self.level = level
        self.numbers = self.level.generate_numbers()
        self.type = question_type
        self.correct_answer = None
        self.user_answer = None
        self.points = 0
        self.time = 0
        self.current_streak = current_streak

        if question_type == "Multiple":
            operator = '*'
            self.question = operator.join(map(str, self.numbers))
            self.correct_answer = numpy.prod(self.numbers)


    def ask(self):
        io.send("question", question=self.question, time=self.level.time)

        answered = False
        while not answered:
            self.user_answer, self.time = Question.get_answer()
            if self.user_answer is None:
                Game.help()
            else:
                answered = True

        self._calculate_points()


    def _calculate_points(self):
        if self.correct and self.in_time:
            self.points += int(self.level.level * 100 / self.time)
        else:
            self.points -= 100


    @property
    def correct(self):
        return self.user_answer == self.correct_answer


    @property
    def in_time(self):
        return self.time <= self.level.time


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
        question_data = (self.level.level, self.points, self.current_streak, self.time, self.question, self.user_answer, self.correct_answer, self.correct, self.in_time)
        with log.DatabaseConnection('questions') as db:
            db.append(question_data)


class Game(object):
    def __init__(self, name, start_level=1):
        self.current_streak = 0
        self.max_streak = 0
        self.total_points = 0
        self.total_time = 0
        self.name = name
        self.level = Level(start_level)
        self.question = None

        io.send("welcome", name=self.name)


    def run(self):
        self.ask_question()

        self.try_exit()
        self.question.log()

        self.total_points += self.question.points
        self.total_time += self.question.time
        self._calculate_streak()

        if self.question.correct and self.question.in_time:
            io.send("success")
        elif not self.question.in_time:
            io.send("time failure", self.question.correct_answer)
        elif not self.question.correct:
            io.send("failure", self.question.correct_answer)

        if self.current_streak > 3:
            io.send("streak", streak=self.current_streak)

        io.send("points", points=self.total_points, end=' ')
        io.send("time", time=self.question.time)
        io.send("question end")

        self._calculate_level()
        self.run()


    def _calculate_streak(self):
        if self.question.correct and self.question.in_time:
            self.current_streak += 1
        else:
            self.current_streak = 0

        self.max_streak = max(self.max_streak, self.current_streak)


    def _calculate_level(self):
        if not (self.question.correct and self.question.in_time):
            self.level = Level(max(1, self.level.level - 1))
        elif self.current_streak % 5 == 0 and self.current_streak and self.level.level < NUMBER_OF_LEVELS:
            self.level = Level(self.level.level + 1)
            io.send("level up", level=self.level.level)

    def log(self):
        game_data = (self.name, self.level.level, self.total_points, self.total_time, self.max_streak)
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