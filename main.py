import urllib

from BeautifulSoup import BeautifulSoup
from py_bing_search import PyBingWebSearch


bing_api_key = '6gmJGqJOlN6VmeMkp0j4iA46Ayetcjz49YUfBh/7Nc4'
search_term = "Python Software Foundation"

bing = PyBingWebSearch(bing_api_key, search_term, web_only=False)
search_result = bing.search(format='json')
for page in search_result:
    # TODO: Check if URL is in Database, if not do your job, if the url is already there restart
    '''
    html_stream = urllib.urlopen(page.url)
    soup = BeautifulSoup(html_stream)
    keywords = soup.findAll(attrs={"name": "keywords"})
    print keywords
    '''
    print page.url

#html_stream = urllib.urlopen("http://www.python.org/")
#print html_stream.read()
#soup = BeautifulSoup(html_stream)
#keywords = soup.findAll(attrs={"name": "keywords"})
#print keywords
