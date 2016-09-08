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
maximum_bing_searches = 100
stop_error_number = 10
sleep_time = 20
sleep_time_plus_minus = 5
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           'Accept-Encoding': 'deflate'}
language_subdomain = "de"
logging.basicConfig(level=logging.INFO)
logging.getLogger("requests").setLevel(logging.WARNING)

# DB
db = Processed("ach.sqlite", "processed")

# BING
bing_api_key = '6gmJGqJOlN6VmeMkp0j4iA46Ayetcjz49YUfBh/7Nc4'
search_term = 'site:www.aliexpress.com/store/ inbody:"Get coupon now"'

# DO
bing = PyBingWebSearch(bing_api_key, search_term, web_only=False)
while maximum_bing_searches > 0:
    maximum_bing_searches -= 1

    search_result = bing.search(format='json')
    for page in search_result:
        url = page.url.replace("www.", "{0}.".format(language_subdomain))
        logging.info(url)
        try:
            id = re.match('.*store/(\d+).*', url).group(1)
            if not db.get_is_processed(id):
                html = requests.get(url, headers=headers).text
                soup = BeautifulSoup(html)
                shop = soup.find("span", {"class": "shop-name"}).a.text
                keywords = soup.find(attrs={"name": "keywords"})["content"]
                coupons = []
                for coupon in soup.findAll("a", {"class": "get-coupon-btn"}):
                    discount = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "pay"}))).group(1)
                    minimum_purchase = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "get"}))).group(1)
                    coupons.append(float(minimum_purchase) - float(discount))
                if len(coupons) is not 0:
                    db.save(id, shop, keywords, url, discount, minimum_purchase, min(coupons))
                    logging.info("Saved with coupon.")
                else:
                    db.save(id, shop, keywords, url, None, None, None)
                    logging.info("Saved without coupon.")

                sleep = random.randint(sleep_time - sleep_time_plus_minus, sleep_time + sleep_time_plus_minus)
                logging.info("Wait for {0} Seconds.".format(sleep))
                time.sleep(sleep)
            else:
                logging.info("Already done.")

        except Exception as e:
            logging.error("{1}".format(url, str(e)))
            stop_error_number -= 1
            if stop_error_number < 0:
                sys.exit("To many errors!")
