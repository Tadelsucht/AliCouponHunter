import logging

import re
import requests
import time
from BeautifulSoup import BeautifulSoup
from py_bing_search import PyBingWebSearch
from Database.Table.Processed import Processed

# Config
stop_error_number = 10
sleep_time = 5
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           'Accept-Encoding': 'deflate'}
language_subdomain = "de"

# DB
db = Processed("ach.sqlite", "processed")

# BING
bing_api_key = '6gmJGqJOlN6VmeMkp0j4iA46Ayetcjz49YUfBh/7Nc4'
search_term = 'site:www.aliexpress.com/store/ inbody:"Get coupon now"'

# DO
bing = PyBingWebSearch(bing_api_key, search_term, web_only=False)
search_result = bing.search(format='json')
for page in search_result:
    url = page.url.replace("www.", "{0}.".format(language_subdomain))
    logging.info(url)
    try:
        if db.get_is_processed(url):
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
                db.save(shop, keywords, url, min(coupons))
            else:
                db.save(shop, keywords, url, None)
    except Exception as e:
        logging.error("{0}: {1}".format(url, str(e)))
        stop_error_number -= 1
        if stop_error_number < 0:
            logging.critical("To many errors!")
            break
        time.sleep(sleep_time)
