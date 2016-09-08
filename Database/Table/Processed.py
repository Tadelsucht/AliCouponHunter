from datetime import datetime
from Database.Database import Database


class Processed(Database):
    _sql_table = u'''CREATE TABLE {0} (Shop TEXT, Keywords TEXT, URL TEXT, BestCouponDifference TEXT, AddedOrUpdated TIMESTAMP)'''

    def save(self, shop, keywords, url, bcd):
        self._cursor.execute(
            u"INSERT INTO {0} (Shop, Keywords, URL, BestCouponDifference, AddedOrUpdated) VALUES (?,?,?,?,?);".format(
                self._database_name),
            (shop, keywords, url, bcd, datetime.now()))
        self._connection.commit()

    def get_is_processed(self, url):
        self._cursor.execute("SELECT COUNT(URL) FROM {0} WHERE URL = ?".format(self._database_name), [url])
        if self._cursor.fetchone() > 0:
            return True
        return False
