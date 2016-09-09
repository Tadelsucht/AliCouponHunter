from datetime import datetime
from Database.Database import Database


class Processed(Database):
    _sql_table = u'''CREATE TABLE {0} (ID INT PRIMARY KEY, Shop TEXT, Keywords TEXT, URL TEXT, Discount DOUBLE, MinimumPurchase DOUBLE, BestCouponDifference DOUBLE, CheapestItem Text, CheapestItemPrice DOUBLE, AddedOrUpdated TIMESTAMP)'''

    def save(self, id, shop, keywords, url, discount, minimum_purchase, bcd, cheapest_item, cheapest_item_price):
        self._cursor.execute(
            u"INSERT INTO {0} (ID, Shop, Keywords, URL, Discount, MinimumPurchase, BestCouponDifference, CheapestItem, CheapestItemPrice, AddedOrUpdated) VALUES (?,?,?,?,?,?,?,?,?,?);".format(
                self._database_name),
            (id, shop, keywords, url, discount, minimum_purchase, bcd, cheapest_item, cheapest_item_price, datetime.now()))
        self._connection.commit()

    def get_is_processed(self, url):
        self._cursor.execute("SELECT COUNT(*) FROM {0} WHERE ID = ?".format(self._database_name), [url])
        if self._cursor.fetchone()[0] == 0:
            return False
        return True
