# coding: utf8
########## Import ##########
import logging
import random
import re
import io
import requests
import time
import sys
from BeautifulSoup import BeautifulSoup
from py_bing_search import PyBingWebSearch
from Database.Table.Processed import Processed

########## Config ##########
STOP_CONSECUTIVELY_ERROR_NUMBER = 10
SLEEP_TIME = 6
SLEEP_TIME_PLUS_MINUS = 3
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           "Accept-Language": "de",
           'Accept-Encoding': 'deflate'}
SHOP_SEARCH_ITEM_PHRASES_FILE = "shop_search_item_phrases.txt"
FORBIDDEN_ITEMS_PHRASES_FILE = 'forbidden_item_phrases.txt'
DB_FILE = "ach.sqlite"
MAXIMAL_ALREADY_SCANNED_IN_A_ROW_BEFORE_NEXT_WORD = 2000


########## Functions ##########
def get_list_from_file(file):
    with io.open(file, 'r', encoding='utf8') as f:
        list = f.readlines()
        list = map(lambda s: s.strip(), list)
        return list


def sleep_to_prevent_ban():
    sleep = random.randint(SLEEP_TIME - SLEEP_TIME_PLUS_MINUS, SLEEP_TIME + SLEEP_TIME_PLUS_MINUS)
    logging.info("Wait for {0} Seconds.".format(sleep))
    time.sleep(sleep)


########## Logging ##########
logging.basicConfig(level=logging.INFO, format='%(asctime)s| %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

########## Variables ##########
SHOP_SEARCH_URL = "http://aliexpress.com/wholesale?SearchText={0}&SortType=default&page={1}"
MOBILE_ITEM_URL = "https://m.aliexpress.com/search.htm?sortType=PP_A&sellerAdminSeq={0}"
FORBIDDEN_ITEMS_PHRASES = get_list_from_file(FORBIDDEN_ITEMS_PHRASES_FILE)

########## Init ##########
db = Processed(DB_FILE, "processed")
db.remove_entries_with_forbidden_phrases(FORBIDDEN_ITEMS_PHRASES)

jar = requests.cookies.RequestsCookieJar()
requests_session = requests.Session()
requests_session.headers = HEADERS
error_counter = 0
item_phrases = get_list_from_file(SHOP_SEARCH_ITEM_PHRASES_FILE)
links_checked = 0

########## DO ##########
def possible_error_exit():
    if error_counter > STOP_CONSECUTIVELY_ERROR_NUMBER:
        sys.exit("Stop because to many errors!")


# TODO: Start Info. Wie viele sind in der Datenbank?
for phrase in item_phrases:
    logging.info(
        "Links checked: {0} | Words: {1}/{2}".format(links_checked, item_phrases.index(phrase) + 1, len(item_phrases)))

    already_scanned_in_a_row = 0
    page = 0
    shops = []
    while already_scanned_in_a_row < MAXIMAL_ALREADY_SCANNED_IN_A_ROW_BEFORE_NEXT_WORD:
        ignore_equality = False
        page += 1

        try:
            url = SHOP_SEARCH_URL.format(phrase, page)
            logging.info("Item phrase: {0} | Page: {1} | Already scanned in a row: {2} | URL: {3}".format(phrase, page, already_scanned_in_a_row, url))
            html = requests_session.get(
                url,
                headers=HEADERS).text
            shops = re.findall(ur'(aliexpress.com/store/\d+)"', html)

            if len(shops) == 0:
                logging.error("No search results.")
                error_counter += 1
        except:
            logging.error(str(e))
            error_counter += 1

        links_checked_before = links_checked
        for shop_url in shops:
            links_checked += 1
            try:
                http_shop_url = "http://" + shop_url
                logging.info("Current URLs: {0}/{1} | Url: {2}".format(links_checked - links_checked_before,
                                                                       len(shops), http_shop_url))
                id = re.match('.*store/(\d+).*', http_shop_url).group(1)
                if not db.get_is_processed(id):
                    logging.error("Get Coupons.")
                    html = requests_session.get(http_shop_url, headers=HEADERS).text
                    soup = BeautifulSoup(html)

                    # Info
                    shop = soup.find("span", {"class": "shop-name"}).a.text
                    keywords = soup.find(attrs={"name": "keywords"})["content"]

                    # Coupon
                    best_discount = None
                    best_minimum_purchase = None
                    best_coupon_difference = None
                    for coupon in soup.findAll("a", {"class": "get-coupon-btn"}):
                        discount = float(
                            re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "pay"}))).group(1))
                        minimum_purchase = float(
                            re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "get"}))).group(1))
                        coupon_difference = float(minimum_purchase) - float(discount)
                        if best_coupon_difference is None or coupon_difference < best_coupon_difference or (
                                        coupon_difference is best_coupon_difference and best_discount < discount):
                            best_discount = discount
                            best_minimum_purchase = minimum_purchase
                            best_coupon_difference = coupon_difference

                    # Sleep Coupon
                    sleep_to_prevent_ban()

                    # Cheapest Item
                    logging.error("Get cheapest item.")
                    mobile_id = re.search(r'.*ownerMemberId: \'(\d+)\'.*', html).group(1)
                    mobile_url = MOBILE_ITEM_URL.format(
                        mobile_id)
                    mobile_html = requests_session.get(mobile_url).text
                    cheapest_item = None
                    cheapest_item_price = None
                    items = re.findall(
                        ur'subject":"([\w\s ÄÖÜäöüß\!]+)((?!subject).)*promoMaxAmount":{"value":([\d\.]+)((?!promoMaxAmount).)*minAmount":{"value":([\d\.]+)',
                        mobile_html)
                    for item in items:
                        item_name = item[0]
                        item_price = float(item[2].encode("ascii", "ignore"))
                        if item_price == 0.01:  # Default promo is 0.01, use other value for this case
                            item_price = float(item[4].encode("ascii", "ignore"))
                        if cheapest_item_price is None or item_price < cheapest_item_price:
                            if any(word.lower() in item_name.lower() for word in FORBIDDEN_ITEMS_PHRASES):
                                logging.info("Filtered phrase was found.")
                            else:
                                cheapest_item = item_name
                                cheapest_item_price = item_price

                    # TODO: Versandkosten aufzeichnen btw. yes and no

                    # Save
                    db.save(id, shop, keywords, http_shop_url, best_discount, best_minimum_purchase,
                            best_coupon_difference,
                            cheapest_item, cheapest_item_price)
                    if best_coupon_difference is not None:
                        logging.info(
                            "Saved with coupon. | Difference: {0:.2f} | Discount: {1} | Minimum purchase: {2} | Price of cheapest item: {3}".format(
                                best_coupon_difference, best_discount, best_minimum_purchase, cheapest_item_price))
                    else:
                        logging.info("Saved without coupon. | Price of cheapest item: {0}".format(cheapest_item_price))

                    # Sleep Coupon
                    sleep_to_prevent_ban()

                    # Reset Error Counter
                    error_counter = 0

                    # Reset already scanned counter
                    already_scanned_in_a_row = 0
                else:
                    logging.info("Already scanned.")
                    already_scanned_in_a_row += 1
            except Exception as e:
                logging.error("{1}".format(http_shop_url, str(e)))
                error_counter += 1

                # Error exit
                possible_error_exit()

        # Error exit
        possible_error_exit()

        # Sleep Search
        sleep_to_prevent_ban()

        # Todo: Nachdem ein phrase komplett durchleutet wurde, wird der eintrag aus der datei gelöscht und in die alrady_searched getan
