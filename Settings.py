__author__ = 'Kfir'

import log

SYSTEM_TABLES = ['levels']
USER_DATA_TABLES = ['questions', 'games']


def delete_database():
    db_path = log.DB_PATH

    for table in USER_DATA_TABLES:
        _delete_table(table)


def _delete_table(table, keep_headers=True):
    index = 1
    if keep_headers:
        index += 1

    with log.DatabaseConnection(table) as table:
        for _ in range(table.ws.max_row - 1):
            table.ws.delete_rows(index, 1)