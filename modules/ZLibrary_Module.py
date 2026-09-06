import requests
from bs4 import BeautifulSoup
from nicegui import ui
import utils
import time

MODULE_INFO = {
    'id': 'zlibrary',
    'display_name': 'Z-Library',
    'base_url': 'https://z-lib.sk/s/',
    'enabled': True,
    'version': '1.0.0',
    'internal_page': False,
    'requires_extension': True,
    'icon': 'sports_esports',
    'color': '#1e88e5',
    'timeout': 120,
    'rate_limit_seconds': 1.0,
    'direct_link': False
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
}

def build_link(search):
    url = MODULE_INFO['base_url'] + search
    return url

def displayInternalPage(selectedUrl: str):
    """Function used to display a custom page (eg. nested links) called after selecting a result from the main page"""
    pass

def getSoup(website: str) -> BeautifulSoup | None:
    """Given an url, return the soup of it using requests"""
    try:
        r = requests.get(url=website, headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"Status code for {website} is {r.status_code}")
        soup = BeautifulSoup(r.content, "html.parser")
        return soup
    except Exception as e:
        print(e)
        return None

def getLinks(search, url):
    url += search
    print(f"Searching for {url}")
    html = None
    while html == None:
        print(f"Searching for {url.replace(" ", "%20")}")
        html = utils.get_cached_html(url=url.replace(" ", "%20"))
        time.sleep(0.5)
    utils.delete_cached_html(MODULE_INFO['base_url'])
    soup = BeautifulSoup(html, "html.parser")
    if not soup: return
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
    print(soup.prettify())
    
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('pokemon', MODULE_INFO['base_url'])
    print(res)