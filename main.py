# coding: utf8
########## Import ##########
import logging
import random
import re
import io
from datetime import datetime, timedelta
import requests
import time
import sys
from BeautifulSoup import BeautifulSoup
from Database.Table.Processed import Processed

########## Config ##########
STOP_CONSECUTIVELY_ERROR_NUMBER = 10
SLEEP_TIME = 4
SLEEP_TIME_PLUS_MINUS = 1
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           "Accept-Language": "de",
           'Accept-Encoding': 'deflate'}
SHOP_SEARCH_ITEM_PHRASES_FILE = "shop_search_item_phrases.txt"
ALREADY_SEARCHED_SHOP_SEARCH_ITEM_PHRASES_FILE = "already_searched_shop_search_item_phrases.txt"
FORBIDDEN_ITEMS_PHRASES_FILE = 'forbidden_item_phrases.txt'
DB_FILE = "ach.sqlite"
MAXIMAL_ALREADY_SCANNED_IN_A_ROW_BEFORE_NEXT_WORD = 1000
NO_SEARCH_RESULTS_COUNTER_MAX = 10
EXPIRED_BEFORE_EQUAL_DATETIME = datetime.strptime("2016-09-12 11:00:00.000000", "%Y-%m-%d %H:%M:%S.%f")
EXPIRED_ONLY_WITH_COUPON = True
SHOP_SEARCH_URL = "http://aliexpress.com/wholesale?SearchText={0}&SortType=price_asc&groupsort=0&isFreeShip=y&page={1}"
MOBILE_ITEM_URL = "https://m.aliexpress.com/search.htm?sortType=PP_A&freeshippingType=f&sellerAdminSeq={0}"


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
FORBIDDEN_ITEMS_PHRASES = get_list_from_file(FORBIDDEN_ITEMS_PHRASES_FILE)

########## Init ##########
db = Processed(DB_FILE, "processed")
db.remove_entries_with_forbidden_phrases([p.replace('*', '%') for p in FORBIDDEN_ITEMS_PHRASES])

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


logging.info("Database Info | Already scanned: {0}".format(db.get_number_of_shops()))
for phrase in item_phrases:
    logging.info(
        "Words: {1}/{2}".format(links_checked, item_phrases.index(phrase) + 1, len(item_phrases)))

    no_search_results_counter = 0
    already_scanned_in_a_row = 0
    page = 0
    shops = []
    while already_scanned_in_a_row < MAXIMAL_ALREADY_SCANNED_IN_A_ROW_BEFORE_NEXT_WORD:
        ignore_equality = False
        page += 1

        try:
            url = SHOP_SEARCH_URL.format(phrase, page)
            logging.info(
                "Links checked: {0} | Item phrase: {1} | Page: {2} | Already scanned in a row: {3} | URL: {4}".format(
                    links_checked, phrase, page, already_scanned_in_a_row, url))
            html = requests_session.get(
                url,
                headers=HEADERS).text
            shops = re.findall(ur'(aliexpress.com/store/\d+)"', html)

            if len(shops) == 0:
                logging.error("No search results.")
                no_search_results_counter += 1
                if no_search_results_counter > NO_SEARCH_RESULTS_COUNTER_MAX:
                    break
            else:
                no_search_results_counter = 0
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
                if db.delete_if_older_as_datetime(id, EXPIRED_BEFORE_EQUAL_DATETIME, EXPIRED_ONLY_WITH_COUPON):
                    logging.info("Shop already scanned. But scan was expired.")
                if not db.is_saved(id):
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
                        ur'subject":"([\w\s ÄÖÜäöüß\!\.\,]+)((?!subject).)*promoMaxAmount":{"value":([\d\.]+)((?!promoMaxAmount).)*minAmount":{"value":([\d\.]+)',
                        mobile_html)
                    for item in items:
                        item_name = item[0]
                        item_price = float(item[2].encode("ascii", "ignore"))
                        if item_price == 0.01:  # Default promo is 0.01, use other value for this case
                            item_price = float(item[4].encode("ascii", "ignore"))
                        if cheapest_item_price is None or item_price < cheapest_item_price:
                            forbidden_phrase = None
                            for word in FORBIDDEN_ITEMS_PHRASES:
                                if re.search(("^" + word.lower() + "$").replace("*", ".*"), item_name.lower()) is not None:
                                    forbidden_phrase = word
                                    break

                            if forbidden_phrase is not None:
                                logging.info("Following filtered phrase was found: {0}".format(forbidden_phrase))
                            else:
                                cheapest_item = item_name
                                cheapest_item_price = item_price

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
                logging.error("{0}".format(sys.exc_info()))
                error_counter += 1

                # Error exit
                possible_error_exit()

        # Error exit
        possible_error_exit()

        # Sleep Search
        sleep_to_prevent_ban()

    # Move for item_phrases to already searched
    with io.open(SHOP_SEARCH_ITEM_PHRASES_FILE, 'w', encoding='utf8') as f:
        for phrase in item_phrases[1:]:
            f.write(phrase + "\r\n")
    already_searched_shop_search_item_phrases = get_list_from_file(ALREADY_SEARCHED_SHOP_SEARCH_ITEM_PHRASES_FILE)
    already_searched_shop_search_item_phrases.append(item_phrases[0])
    with io.open(ALREADY_SEARCHED_SHOP_SEARCH_ITEM_PHRASES_FILE, 'w', encoding='utf8') as f:
        for phrase in already_searched_shop_search_item_phrases:
            f.write(phrase + "\r\n")
logging.info("Scannend all words. Script stop.")
