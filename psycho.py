WELCOME_MESSAGE = "Hello {}, and welcome to the psycho app!\r\nYou can exit anytime by typing 'exit'\r\n"
QUESTION_MESSAGE = "What is {} times {}?"
EXIT_REQUEST = "exit"
HELP_REQUEST = "help"
GET_ANSWER_MESSAGE = "Your answer: "
HELP_MESSAGE = "Please answer with numbers only.\r\nTo exit, please type 'exit'"
SUCCESFUL_MESSAGE = "Hooray!"
RESULT_MESSAGE_FORMAT = "{}\r\n{}. {}"
FAILURE_MESSAGE = "incorrect, the answer is {}, better luck next time!"
TIMING_MESSAGE_FORMAT = "Elapsed time: {}"
STREAK_MESSAGE_FORMAT = "You got {} in a row!"
QUIT_MESSAGE = "Thank you and goodbye!"
DEFAULT_NAME = "Lilya"

from random import randint
from datetime import datetime
from functools import wraps
import sys


def exit_game():
	print QUIT_MESSAGE
	sys.exit()


def help():
	print HELP_MESSAGE


def timing(f):
	@wraps(f)
	def wrapper(*args, **kwargs):
		start = datetime.now()
		result = f(*args, **kwargs)
		time_diff = datetime.now() - start
		return result, time_diff.seconds
	return wrapper


def generate_numbers(start=1, end=20, numbers=2):
	return [randint(start, end) for i in range(numbers)]


def get_answer():
	user_input = raw_input(GET_ANSWER_MESSAGE)

	if user_input.isdigit():
		return int(user_input)
	elif user_input == EXIT_REQUEST:
		return exit_game()
	else:
		help()
		return get_answer()


@timing
def question():
	a, b = generate_numbers()
	answer = None

	print QUESTION_MESSAGE.format(a, b)
	answer = get_answer()

	if answer == a * b:
		return True, SUCCESFUL_MESSAGE
	
	return False, FAILURE_MESSAGE.format(a*b)

def print_result(result_message, time, row):
	if row > 3:
		streak_message = STREAK_MESSAGE_FORMAT.format(row)
	else:
		streak_message = ""

	timing_message = TIMING_MESSAGE_FORMAT.format(time)

	print RESULT_MESSAGE_FORMAT.format(result_message, timing_message, streak_message)


def main(name=DEFAULT_NAME):
	print WELCOME_MESSAGE.format(DEFAULT_NAME)
	exit = False
	row = 0

	while not exit:
		(good_answer, result_message), time = question()
		row = row + 1 if good_answer else 0

		print_result(result_message, time, row)

		print

	exit_game()



if __name__ == "__main__":
	main()
	raw_input()