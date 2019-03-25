__author__ = 'Kfir'
import csv

DB_PATH = "database\\"
FILE_FORMAT = '.csv'


class DatabaseConnection(object):
    def __init__(self, table, directory=DB_PATH):
        self.path = directory + table + FILE_FORMAT
        self.file = None


    def __enter__(self):
        self.file = open(self.path, 'a+', newline='')
        return self


    def __exit__(self, exception_type, exception_value, traceback):
        self.file.close()


    def append(self, data):
        writer = csv.writer(self.file, delimiter=',')
        writer.writerow(data)


    def read(self, read_type='raw'):
        self.file.seek(0)
        if read_type == 'dict':
            data = list(csv.DictReader(self.file, delimiter=','))
        elif read_type == 'raw':
            data = self.file.read()
        return data
