__author__ = 'Kfir'
import os

DEFAULT_PATH = "GameDB.csv"


class DatabaseConnection(object):
    def __init__(self, path=DEFAULT_PATH):
        self.path = path
        self.file = None


    def __enter__(self):
        self.file = open(self.path, 'a+')
        return self


    def __exit__(self):
        self.file.close()


    def append(self, item):
        self.file.write(item + '\n')

