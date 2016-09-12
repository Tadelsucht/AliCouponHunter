# coding: utf8
import logging
from datetime import datetime
from Database.Database import Database


class Processed(Database):
    _sql_table = u'''CREATE TABLE {0} (ID INT PRIMARY KEY, Shop TEXT, Keywords TEXT, URL TEXT, Discount DOUBLE, MinimumPurchase DOUBLE, BestCouponDifference DOUBLE, CheapestItem Text, CheapestItemPrice DOUBLE, AddedOrUpdated TIMESTAMP)'''

    def save(self, id, shop, keywords, url, discount, minimum_purchase, bcd, cheapest_item, cheapest_item_price):
        self._cursor.execute(
            u"INSERT INTO {0} (ID, Shop, Keywords, URL, Discount, MinimumPurchase, BestCouponDifference, CheapestItem, CheapestItemPrice, AddedOrUpdated) VALUES (?,?,?,?,?,?,?,?,?,?);".format(
                self._database_name),
            (id, shop, keywords, url, discount, minimum_purchase, bcd, cheapest_item, cheapest_item_price,
             datetime.now()))
        self._connection.commit()

    def is_saved(self, url):
        self._cursor.execute("SELECT COUNT(*) FROM {0} WHERE ID = ?".format(self._database_name), [url])
        if self._cursor.fetchone()[0] == 0:
            return False
        return True

    def remove_entries_with_forbidden_phrases(self, forbidden_item_phrases):
        query = u''' FROM {0} WHERE '''.format(self._database_name)
        if len(forbidden_item_phrases) is 0:
            return
        for phrase in forbidden_item_phrases:
            query += u' CheapestItem LIKE "{0}" OR'.format(phrase)
        query = query[:-2]
        self._cursor.execute(u"SELECT COUNT(*) " + query)
        logging.info(u"Number of deleted forbidden entries: {0}".format(self._cursor.fetchone()[0]))
        self._cursor.execute(u"DELETE " + query)

    def get_number_of_shops(self):
        self._cursor.execute(u"SELECT COUNT(*) FROM {0}".format(self._database_name))
        return self._cursor.fetchone()[0]

    def delete_if_older_as_datetime(self, id, datetime_obj, has_coupon):
        return_value = False

        query = " FROM {0} WHERE ID = ? AND AddedOrUpdated <= date(?) ".format(self._database_name)
        if has_coupon:
            query += " AND Discount IS NOT NULL "

        self._cursor.execute("SELECT COUNT(*) " + query, (id, str(datetime_obj)))
        if self._cursor.fetchone()[0] != 0:
            return_value = True

        self._cursor.execute(
            "DELETE " + query,
            (id, str(datetime_obj)))

        return return_value