__author__ = 'Kfir'

MESSAGE = {"help":    "Please answer with numbers only.\r\nTo exit, please type 'exit'",
           "welcome": "Hello {name}, and welcome to the psycho app!\r\nYou can exit anytime by typing 'exit'\r\n",
           "quit":    "Thank you and goodbye!",
           "failure": "incorrect, the answer is {}, better luck next time!",
           "success": "Hooray!",
           "answer" : "Your answer: ",
           "time":    "Elapsed time: {time}",
           "streak":  "You got {streak} in a row!",
           "question multiple": "What is {} times {}?"
           }
LB = '\n'


def send(message, *args, **kwargs):
    if 'end' in kwargs.keys():
        end = kwargs['end']
    else:
        end = LB

    if 'raw' in kwargs.keys():
        kwargs.pop('raw')
        print(message.format(*args, **kwargs), end=end)
    else:
        print(MESSAGE[message].format(*args, **kwargs), end=end)


def receive(message=None, *args, **kwargs):
    kwargs["end"] = ''
    send(message, *args, **kwargs)
    return input()