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
    'internal_page': True,
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

def internalPage(selectedUrl: str):
    """Function used to display a custom page (eg. nested links) called after selecting a result from the main page"""
    html = None
    while html == None:
        html = utils.get_cached_html(url=selectedUrl.replace(" ", "%20"))
        print(f"Looking for {selectedUrl.replace(" ", "%20")} key")
        time.sleep(0.5)
    soup = BeautifulSoup(html, "html.parser")
    link = soup.find_all("a", {"class": "btn btn-default dlButton addDownloadedBook"})[0]
    return("https://z-lib.sk/" + str(link.get('href')))

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
        html = utils.get_cached_html(url=url.replace(" ", "%20"))
        time.sleep(0.5)
    utils.delete_cached_html(MODULE_INFO['base_url'])
    soup = BeautifulSoup(html, "html.parser")
    if not soup: return
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
    resultContainer = soup.find_all("div", {"id": "searchResultBox"})[0]
    books = resultContainer.select("div.book-item")
    for book in books:
        results['images'].append(book.find_all('img')[0].get('data-src', default="https://z-lib.sk/img/cover-not-exists.png"))
        results['titles'].append(book.find_all("div", {"slot": "title"})[0].text)
        z_bookcard = book.find_all("z-bookcard")[0]
        results['links'].append("https://z-lib.sk/" + str(z_bookcard.get('href')))
        results['descriptions'].append(
            str(z_bookcard.get('isbn')) + ' - ' + 
            str(z_bookcard.get('publisher')) + ' - ' + 
            str(z_bookcard.get('language')) + ' - ' + 
            str(z_bookcard.get('year')) + ' - ' +
            str(z_bookcard.get('extension')) + ' - ' +
            str(z_bookcard.get('filesize')) + ' - ' +
            str(z_bookcard.get('rating')) + ' - ' +
            str(z_bookcard.get('quality')))
        results['badges'].append('NULL')
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('pokemon', MODULE_INFO['base_url'])
    print(res)