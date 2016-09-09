import logging
import random

import re
import requests
import time

import sys
from BeautifulSoup import BeautifulSoup
from py_bing_search import PyBingWebSearch
from Database.Table.Processed import Processed

# Config
maximum_bing_searches = 1000
stop_consecutively_error_number = 5
sleep_time = 15
sleep_time_plus_minus = 5
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           'Accept-Encoding': 'deflate'}
language_subdomain = "de"
logging.basicConfig(level=logging.INFO, format='%(asctime)s| %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)

# DB
db = Processed("ach.sqlite", "processed")

# BING
bing_api_key = '9/y/HMPWxhiYA2W5VXejrHvQkkdwNJb0+vvo7Skdfuc'
search_term = 'site:www.aliexpress.com/store/ inbody:"Get coupon now"'

# DO
jar = requests.cookies.RequestsCookieJar()
requests_session = requests.Session()
requests_session.headers = headers
error_counter = 0
bing = PyBingWebSearch(bing_api_key, search_term, web_only=False)
bing_search_counter = 0


def sleep_to_prevent_ban():
    sleep = random.randint(sleep_time - sleep_time_plus_minus, sleep_time + sleep_time_plus_minus)
    logging.info("Wait for {0} Seconds.".format(sleep))
    time.sleep(sleep)


while bing_search_counter is not maximum_bing_searches:
    logging.info("Links checked: {2} | Bing searches: {0}/{1}".format(bing_search_counter, maximum_bing_searches,
                                                                      bing_search_counter * 50))
    bing_search_counter += 1

    search_result = bing.search(format='json')

    if len(search_result) == 0:
        logging.error("No search results.")
        error_counter += 1

    for page in search_result:
        url = page.url.replace("www.", "{0}.".format(language_subdomain))
        url = re.match('(https?://\w+.aliexpress.com/store/\d+).*', url).group(1)

        logging.info(url)
        try:
            id = re.match('.*store/(\d+).*', url).group(1)
            if not db.get_is_processed(id):
                logging.error("Get Coupons.")
                html = requests_session.get(url, headers=headers).text
                soup = BeautifulSoup(html)

                # Info
                shop = soup.find("span", {"class": "shop-name"}).a.text
                keywords = soup.find(attrs={"name": "keywords"})["content"]

                # Coupon
                best_discount = None
                best_minimum_purchase = None
                best_coupon_difference = None
                for coupon in soup.findAll("a", {"class": "get-coupon-btn"}):
                    discount = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "pay"}))).group(1)
                    minimum_purchase = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "get"}))).group(1)
                    coupon_difference = float(minimum_purchase) - float(discount)
                    if best_coupon_difference is None or coupon_difference < best_coupon_difference or (
                                    coupon_difference is best_coupon_difference and best_discount < discount):
                        best_discount = discount
                        best_minimum_purchase = minimum_purchase
                        best_coupon_difference = coupon_difference

                # Sleep
                sleep_to_prevent_ban()

                # Cheapest Item
                logging.error("Get cheapest item.")
                mobile_id = re.search(r'.*ownerMemberId: \'(\d+)\'.*', html).group(1)
                mobile_url = "https://m.{0}.aliexpress.com/search.htm?sortType=PP_A&sellerAdminSeq={1}".format(
                    language_subdomain, mobile_id)
                mobile_html = requests_session.get(mobile_url).text
                cheapest_item = None
                items = re.findall(r'promoMaxAmount":{"value":([\d\.]+)', mobile_html)
                for item in items:
                    item = float(item)
                    if cheapest_item is None or item < cheapest_item:
                        cheapest_item = item

                # Save
                db.save(id, shop, keywords, url, best_discount, best_minimum_purchase, best_coupon_difference,
                        cheapest_item)
                if best_coupon_difference is not None:
                    logging.info("Saved with coupon. | Difference: {0:.2f} | Discount: {1} | Cheapest item: {2}".format(
                        best_coupon_difference, best_discount, cheapest_item))
                else:
                    logging.info("Saved without coupon.")

                # Sleep
                sleep_to_prevent_ban()

                # Reset Error Counter
                error_counter = 0
            else:
                logging.info("Already done.")

        except Exception as e:
            logging.error("{1}".format(url, str(e)))
            error_counter += 1

        if error_counter > stop_consecutively_error_number:
            sys.exit("Stop because to many errors!")
