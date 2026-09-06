from urllib.parse import urljoin

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
    """Function used to return an instance of DownloadInfo (eg. for multiple links/mirrors) called after selecting a result from the main page"""
    html = None
    while html == None:
        html = utils.get_cached_html(url=selectedUrl.replace(" ", "%20"))
        print(f"Looking for {selectedUrl.replace(" ", "%20")} key")
        time.sleep(0.5)
    soup = BeautifulSoup(html, "html.parser")
    
    title_el = soup.select_one('h1.book-title')
    title = title_el.get_text(strip=True) if title_el else 'Unknown'

    img_el = soup.select_one('z-cover img')
    image = str(img_el.get('src')) if img_el and str(img_el.get('src')) else None
    if image and 'cover-not-exists.png' in image:
        image = "https://z-lib.sk" + image
    
    details: dict[str, str] = {}
 
    author_el = soup.select_one('i.authors a')
    if author_el:
        details['Author'] = author_el.get_text(strip=True)
 
    for prop in soup.select('.bookDetailsBox .bookProperty'):
        label_el = prop.select_one('.property_label')
        value_el = prop.select_one('.property_value')
        if label_el and value_el:
            label = label_el.get_text(strip=True).rstrip(':')
            value = value_el.get_text(strip=True)
            details[label] = value
    links: list[utils.DownloadLink] = []
 
    main_dl = soup.select_one('a.dlButton.addDownloadedBook[href^="/dl/"]')
    if main_dl and main_dl.get('href'):
        ext_el = main_dl.select_one('.book-property__extension')
        ext = ext_el.get_text(strip=True).upper() if ext_el else 'FILE'
        full_text = main_dl.get_text(strip=True)
        size = full_text.split(',', 1)[1].strip() if ',' in full_text else ''
        label = f'{ext} - {size}' if size else ext
        links.append(utils.DownloadLink(label=label, url=urljoin("https://z-lib.sk/", str(main_dl['href']))))
    return utils.DownloadInfo(
        title=title,
        image=image,
        description=None,
        details=details,
        links=links,
        source_url=selectedUrl,
    )

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
        image = book.find_all('img')[0].get('data-src', default="https://z-lib.sk/img/cover-not-exists.png")
        if 'cover-not-exists.png' in str(image):
            results['images'].append("https://z-lib.sk/img/cover-not-exists.png")
        else:
            results['images'].append(image)
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