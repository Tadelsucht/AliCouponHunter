import sqlite3
from abc import ABCMeta


class Database:
    __metaclass__ = ABCMeta

    _sql_table = u'''TABLE DEFINITION'''

    def __init__(self, database_file, database_name):
        self._connection = sqlite3.connect(database_file, detect_types=sqlite3.PARSE_DECLTYPES)
        self._database_name = database_name
        self._cursor = self._connection.cursor()
        self._cursor.execute(u'''SELECT name FROM sqlite_master
            WHERE type='table' AND name='%s';''' % self._database_name)
        if self._cursor.fetchone() is None:
            self._cursor.execute(self._sql_table.format(self._database_name))
            self._connection.commit()

    def __del__(self):
        self._connection.close()
