import numpy

EXIT_REQUEST = "exit"
HELP_REQUEST = "help"
RESULT_MESSAGE_FORMAT = "{}\r\n{}. {}"
DEFAULT_NAME = "Lilya"

LEVELS = {"Easy": {"start_num": 1,
                   "end_num":   20,
                   "numbers":   2}
          }


from random import randint
from datetime import datetime
from functools import wraps
import sys
import Interpreter as io


def timing(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        start = datetime.now()
        result = f(*args, **kwargs)
        time_diff = datetime.now() - start
        return result, time_diff.seconds
    return wrapper


class Question(object):
    def __init__(self, question_type="Multiple", level="Easy"):
        self.type = question_type
        parameters = LEVELS[level]
        self.numbers = Question.generate_numbers(**parameters)

        if type == "Multiple":
            self.answer = numpy.prod(self.numbers)
        else:
            self.answer = None


    @staticmethod
    def generate_numbers(start_num=1, end_num=20, numbers=2):
        return [randint(start_num, end_num) for i in range(numbers)]


    def ask(self):
        if self.type == "Multiple":
            io.send("question multiple", *self.numbers)


    def check(self, answer):
        return answer == self.answer


class Game(object):
    def __init__(self, name):
        self.streak = 0
        self.name = name
        io.send("welcome", self.name)


    def run(self):
        quit = False
        while not quit:
            good_answer, time = self.ask_question()
            io.send("time", time=time)

            self.streak = self.streak + 1 if good_answer else 0
            if self.streak > 3:
                io.send("streak", streak=self.streak)

        self.exit_game()


    @staticmethod
    def exit_game():
        io.send("quit")
        sys.exit()


    @staticmethod
    def help():
        io.send("help")


    def get_answer(self):
        user_input = io.receive("answer")

        if user_input.isdigit():
            return int(user_input)
        elif user_input == EXIT_REQUEST:
            return Game.exit_game()
        else:
            help()
            return Game.get_answer()


    @timing
    def ask_question(self):
        question = Question("Multiple", "Easy")
        question.ask()
        answer = self.get_answer()

        if question.check(answer):
            io.send("success")
            return True

        real_answer = question.answer
        io.send("failure", real_answer)
        return False


def main(name=DEFAULT_NAME):
    new_game = Game(name)
    new_game.run()


if __name__ == "__main__":
    main()