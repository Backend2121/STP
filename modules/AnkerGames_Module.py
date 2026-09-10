from typing import Optional

import requests
from bs4 import BeautifulSoup
from utils import Error, ErrorCode

MODULE_INFO = {
    'id': 'ankergames',
    'display_name': 'AnkerGames',
    'base_url': 'https://ankergames.net/search/',
    'website': 'https://ankergames.net/',
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
    pass

def getSoup(website: str) -> BeautifulSoup:
    """Given an url, return the soup of it using requests"""
    r = requests.get(url=website, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"Status code for {website} is {r.status_code}")
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def getLinks(search, url) -> tuple[dict, Optional[Error]]:
    url += search
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}

    try:
        soup = getSoup(url)
    except Exception as e:
        return results, Error.from_code(ErrorCode.WEBSITE_PARSE_FAILED, origin=MODULE_INFO['id'], exception=e)
    articles = soup.select('article.group.relative')
    skipped = 0
    for article in articles:
        title_el = article.select_one('h3')
        title = (title_el.get('title') or title_el.get_text(strip=True)) if title_el else 'NULL'
        if title == 'NULL':
            skipped += 1 

        img_el = article.select_one('picture img')
        image = img_el.get('src') if img_el and img_el.get('src') else 'NULL'
        if title == 'NULL':
            skipped += 1 

        link_el = article.select_one('a[href]')
        link = link_el.get('href') if link_el and link_el.get('href') else 'NULL'
        if link == 'NULL':
            skipped += 1 

        badge_el = article.select_one('span[class*="bg-green-500"]')
        badge = badge_el.get_text(strip=True) if badge_el else 'NULL'
        if badge == 'NULL':
            skipped += 1 

        genre_el = article.select_one('p[title]')
        genre = genre_el.get_text(strip=True) if genre_el else ''
        if genre == '':
            skipped += 1 

        info_el = article.select_one('p[class*="tabular-nums"]')
        info_texts = []
        if info_el:
            info_texts = [
                s.get_text(strip=True)
                for s in info_el.find_all('span')
                if s.get_text(strip=True)
            ]
        if len(info_texts) == 0:
            skipped += 1 

        parts = [p for p in [genre, *info_texts] if p]
        description = ' - '.join(parts) if parts else 'NULL'
        if description == 'NULL':
            skipped += 1 

        results['titles'].append(title)
        results['links'].append(link)
        results['images'].append(image)
        results['descriptions'].append(description)
        results['badges'].append(badge)
    if skipped != 0:
        return results, Error.from_code(ErrorCode.PARTIAL_PARSE_FAILED, origin=MODULE_INFO['id'], msg=f"Failed to parse {skipped} elements")
    return results, None

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('dishonored', "https://ankergames.net/search/")
    print(res)