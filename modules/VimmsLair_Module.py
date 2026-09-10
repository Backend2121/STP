from typing import Optional

import requests
from bs4 import BeautifulSoup

from utils import Error, ErrorCode


MODULE_INFO = {
    'id': 'vimmslair',
    'display_name': 'Vimm\'s Lair',
    'base_url': 'https://vimm.net/vault/?p=list&q=',
    'website': 'https://vimm.net/vault/',
    'enabled': True,
    'version': '1.0.0',
    'internal_page': False,
    'requires_extension': False,
    'icon': 'sports_esports',
    'color': '#1e88e5',
    'timeout': 10,
    'rate_limit_seconds': 1.0,
    'direct_link': False
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
}

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

def getLinks(search, url) -> tuple[dict, Optional[Error]]:
    url += search
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}

    try:
        soup = getSoup("Putul")
    except Exception as e:
        return results, Error.from_code(ErrorCode.WEBSITE_PARSE_FAILED, origin=MODULE_INFO['id'], exception=e)
    if not soup: return results, Error.from_code(ErrorCode.WEBSITE_PARSE_FAILED, origin=MODULE_INFO['id'])
    try:
        table = soup.find_all('table')[0]
        table_entries = table.select("tr")
    except Exception as e:
        return results, Error.from_code(ErrorCode.CORE_PARSING_FAILED, origin=MODULE_INFO['id'], exception=e)
    skipped = 0
    for tr in table_entries:
        try:
            link = tr.find_all("a")[1]
        except IndexError:
            continue
        if not link: 
            skipped += 1
        title = link.text or 'NULL'
        if title == 'NULL': skipped += 1
        results['titles'].append(title)
        link = link.get('href')
        results['links'].append(MODULE_INFO['base_url'].replace("/vault/?p=list&q=", "") + link or 'NULL')
        if title == 'NULL': skipped += 1
        results['images'].append('NULL')
        full_description = ""
        for td in tr.find_all('td'):
            full_description += td.text + " - "
        full_description = full_description.replace(" - 9", " - ")
        results['descriptions'].append(full_description or 'NULL')
        img = tr.find('img')
        if not img:
            results['badges'].append('NULL')
            skipped += 1
        else:
            results['badges'].append("https://vimm.net/" + str(img.get('src')))
    return results, None

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('pokemon', MODULE_INFO['base_url'])
    print(res)