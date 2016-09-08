import sqlite3
from datetime import datetime

class Finds:
    _sql_table = u'''CREATE TABLE {0} (Shop TEXT, Keywords TEXT, URL TEXT, BestCouponDifference TEXT, AddedOrUpdated TIMESTAMP)'''

    def save(self, shop, keywords, url, bcd):
        self._cursor.execute(
            u"INSERT INTO {0} (Shop TEXT, Keywords TEXT, URL TEXT, BestCouponDifference TEXT, AddedOrUpdated) VALUES (?,?,?,?,?);".format(
                self._database_name),
            (shop, keywords, url, bcd, datetime.now()))
        self._connection.commit()
