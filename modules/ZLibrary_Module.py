from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from nicegui import ui
from utils import get_cached_html, delete_cached_html, DownloadInfo, DownloadLink, ErrorCode, Error
import time

MODULE_INFO = {
    'id': 'zlibrary',
    'display_name': 'Z-Library',
    'base_url': 'https://z-lib.sk/s/',
    'website': 'https://z-lib.sk/',
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
        html = get_cached_html(url=selectedUrl.replace(" ", "%20"))
        time.sleep(0.5)
    soup = BeautifulSoup(html, "html.parser")
    
    downloadInfo = DownloadInfo("", None, None, {}, [], None)
    
    skipped = 0
    title = None
    try:
        title_el = soup.select_one('h1.book-title')
        title = title_el.get_text(strip=True) if title_el else 'None'
        if title != 'None':
            downloadInfo.title = title
    except:
        skipped += 1
    image = None
    try:
        img_el = soup.select_one('z-cover img')
        image = str(img_el.get('src')) if img_el and str(img_el.get('src')) else None
        if image and 'cover-not-exists.png' in image:
            image = "https://z-lib.sk" + image
        if image:
            downloadInfo.image = image
    except:
        skipped += 1
    details: dict[str, str] = {}

    try:
        author_el = soup.select_one('i.authors a')
        if author_el:
            details['Author'] = author_el.get_text(strip=True)
    except:
        skipped += 1
    try:
        for prop in soup.select('.bookDetailsBox .bookProperty'):
            label_el = prop.select_one('.property_label')
            value_el = prop.select_one('.property_value')
            if label_el and value_el:
                label = label_el.get_text(strip=True).rstrip(':')
                value = value_el.get_text(strip=True)
                details[label] = value
        downloadInfo.details = details
    except:
        skipped += 1
    links: list[DownloadLink] = []
    try:
        main_dl = soup.select_one('a.dlButton.addDownloadedBook[href^="/dl/"]')
        if main_dl and main_dl.get('href'):
            ext_el = main_dl.select_one('.book-property__extension')
            ext = ext_el.get_text(strip=True).upper() if ext_el else 'FILE'
            full_text = main_dl.get_text(strip=True)
            size = full_text.split(',', 1)[1].strip() if ',' in full_text else ''
            label = f'{ext} - {size}' if size else ext
            links.append(DownloadLink(label=label, url=urljoin("https://z-lib.sk/", str(main_dl['href']))))
    except:
        skipped += 1

    return downloadInfo, None

def getLinks(search, url):
    url += search
    html = None
    # Infinite loop that waits for the web extension to snatch the HTML 
    while html == None:
        html = get_cached_html(url=url.replace(" ", "%20"))
        time.sleep(0.5)
    delete_cached_html(MODULE_INFO['base_url'])
    soup = BeautifulSoup(html, "html.parser")
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
    try:
        resultContainer = soup.find_all("div", {"id": "searchResultBox"})[0]
        books = resultContainer.select("div.book-item")
    except Exception as e:
        return results, Error.from_code(ErrorCode.CORE_PARSING_FAILED, origin=MODULE_INFO['id'], exception=e)
    skipped = 0
    for book in books:
        image = None
        try:
            image = book.find_all('img')[0].get('data-src', default="https://z-lib.sk/img/cover-not-exists.png")
        except Exception as e:
            skipped += 1
        if image and 'cover-not-exists.png' in str(image):
            results['images'].append("https://z-lib.sk/img/cover-not-exists.png")
        else:
            results['images'].append(image)
        try:
            results['titles'].append(book.find_all("div", {"slot": "title"})[0].text)
        except Exception as e:
            skipped += 1
        z_bookcard = None
        try:
            z_bookcard = book.find_all("z-bookcard")[0]
        except Exception as e:
            skipped += 1
        if z_bookcard:
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
    return results, None

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('pokemon', MODULE_INFO['base_url'])
    print(res)