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
headers = {'Accept-Encoding': 'deflate'}

# DB
db = Processed("ach.sqlite", "processed")

# BING
bing_api_key = '6gmJGqJOlN6VmeMkp0j4iA46Ayetcjz49YUfBh/7Nc4'
search_term = 'site:www.aliexpress.com/store/ inbody:"Get coupon now"'

# DO
bing = PyBingWebSearch(bing_api_key, search_term, web_only=False)
search_result = bing.search(format='json')
for page in search_result:
    url = page.url
    if True:
    #try:
        if db.get_is_processed(url):
            html = requests.get(url, headers=headers).text
            soup = BeautifulSoup(html)
            shop = soup.find("span", {"class": "shop-name"}).a.text
            keywords = soup.find(attrs={"name": "keywords"})["content"]
            print keywords
            coupons = []
            for coupon in soup.findAll("a", {"class": "get-coupon-btn"}):
                discount = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "pay"}))).group(1)
                minimum_purchase = re.match('.*\$([0-9\.]+).*', str(coupon.find("span", {"class": "get"}))).group(1)
                coupons.append(float(minimum_purchase) - float(discount))
            #if len(coupons) is not 0:
                #db.save(shop, keywords, url, min(coupons))
            #else:
                #db.save(shop, keywords, url, None)
    '''
    except Exception, e:
        logging.error("{0}: {1}".format(url, str(e)))
        stop_error_number -= 1
        if stop_error_number < 0:
            logging.critical("To many errors!")
            break
        time.sleep(sleep_time)
    '''
    break
