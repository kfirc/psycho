__author__ = 'Kfir'

import openpyxl
import pandas as pd
from itertools import islice
from os import listdir
from os.path import isfile, join, splitext

DB_PATH = "database\\"
FILE_EXTENSION = '.xlsx'


class DatabaseConnection(object):
    def __init__(self, table, directory=DB_PATH):
        self.path = directory + table + FILE_EXTENSION
        self.wb = None
        self.ws = None


    def __enter__(self):
        self.load()
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.save()


    @staticmethod
    def tables():
        all_tables = [splitext(f)[0] for f in listdir(DB_PATH) if isfile(join(DB_PATH, f))]
        return all_tables


    def load(self):
        self.wb = openpyxl.load_workbook(self.path)
        self.ws = self.wb.active


    def save(self, new_path=None):
        if new_path:
            self.wb.save(new_path)
        else:
            self.wb.save(self.path)


    def append(self, data):
        self.ws.append(data)


    def read(self):
        data = self.ws.values
        cols = next(data)[1:]
        data = list(data)
        idx = [r[0] for r in data]
        data = (islice(r, 1, None) for r in data)
        df = pd.DataFrame(data, index=idx, columns=cols)
        return df
