# coding: utf8
import io
import logging
import random

import re
import requests
import time


LANGUAGE_SUBDOMAIN = "de"
SHOP_SEARCH_ITEM_PHRASES_FILE = "shop_search_item_phrases.txt"
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:48.0) Gecko/20100101 Firefox/48.0',
           'Accept-Encoding': 'deflate'}
SLEEP_TIME = 6
SLEEP_TIME_PLUS_MINUS = 3
logging.basicConfig(level=logging.INFO, format='%(asctime)s| %(message)s')
logging.getLogger("requests").setLevel(logging.WARNING)


def get_list_from_file(file):
    with io.open(file, 'r', encoding='utf8') as f:
        list = f.readlines()
        list = map(lambda s: s.strip(), list)
        return list


def sleep_to_prevent_ban():
    sleep = random.randint(SLEEP_TIME - SLEEP_TIME_PLUS_MINUS, SLEEP_TIME + SLEEP_TIME_PLUS_MINUS)
    logging.info("Wait for {0} Seconds.".format(sleep))
    time.sleep(sleep)


jar = requests.cookies.RequestsCookieJar()
requests_session = requests.Session()
requests_session.headers = HEADERS

item_phrases = get_list_from_file(SHOP_SEARCH_ITEM_PHRASES_FILE)
for phrase in item_phrases:
    first_page_shops = None
    current_page_shops = None
    page = 0
    while current_page_shops is None or current_page_shops != first_page_shops:
        page += 1
        logging.info("Item phrase: {0} | Page: {1}".format(phrase, page))

        html = requests_session.get("http://aliexpress.com/wholesale?SearchText={1}&SortType=price_asc&page={2}".format(LANGUAGE_SUBDOMAIN, phrase, page), headers=HEADERS).text
        current_page_shops = re.findall(ur'(aliexpress.com/store/\d+)"',html)
        for url in current_page_shops:
            pass
            #print url

        sleep_to_prevent_ban()