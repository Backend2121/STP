import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from utils import get_cached_html, delete_cached_html, DownloadInfo, DownloadLink, ErrorCode, Error
import time
from utils import DownloadInfo, DownloadLink


MODULE_INFO = {
    'id': '1337x',
    'display_name': '1337x',
    'base_url': 'https://1337x.to/search/',
    'website': 'https://1337x.to/',
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
    url = MODULE_INFO['base_url'] + search + '/1/'
    return url

def internalPage(selectedUrl: str):
    """Function used to return an instance of DownloadInfo (eg. for multiple links/mirrors) called after selecting a result from the main page"""
    html = None
    while html == None:
        html = get_cached_html(url=selectedUrl.replace(" ", "%20"))
        time.sleep(0.5)
    soup = BeautifulSoup(html, "html.parser")

    downloadInfo = DownloadInfo("", None, None, {}, [], None)

    # Title
    skipped = 0
    title = None
    try:
        title_el = soup.find('h1')
        if title_el:
            title = title_el.get_text(strip=True)
        else:
            strong_el = soup.select_one('#description strong')
            title = strong_el.get_text('', strip=True) if strong_el else 'None'
        downloadInfo.title = title
    except:
        skipped += 1

    # Images
    image = None
    try:
        og_image = soup.find('meta', property='og:image')
        image = og_image.get('content') if og_image else None
        downloadInfo.image = str(image)
    except:
        skipped += 1

    # Details
    details = {}
    try:
        for li in soup.select('ul.list li'):
            label_el = li.find('strong')
            value_el = li.find('span')
            if label_el and value_el:
                label = label_el.get_text(strip=True)
                value = value_el.get_text(' ', strip=True)
                if label and value:
                    details[label] = value
        downloadInfo.details = details
    except:
        skipped += 1

    # Description
    description = None
    try:
        desc_el = soup.select_one('#description')
        if desc_el:
            text = desc_el.get_text('\n', strip=True)
            text = re.sub(r'\n{3,}', '\n\n', text) 
            description = text or None
        downloadInfo.description = description
    except:
        skipped += 1

    # Links
    links = []
    try:
        magnet_el = soup.select_one('a[href^="magnet:"]')
        if magnet_el:
            links.append(DownloadLink('Magnet', str(magnet_el['href'])))
    except:
        skipped += 1
    try:
        for a in soup.select('ul.dropdown-menu a[target="_blank"]'):
            label = a.get_text(strip=True)
            href = a.get('href')
            if href:
                links.append(DownloadLink(label, str(href)))
    except:
        skipped += 1
    downloadInfo.links = links
    if skipped != 0:
        return downloadInfo, Error.from_code(ErrorCode.PARTIAL_PARSE_FAILED, origin=MODULE_INFO['id'], msg=f"Failed to parse {skipped} elements")
 
    return downloadInfo, None


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
    url += search + '/1/'
    html = None
    while html == None:
        html = get_cached_html(url=url.replace(" ", "%20"))
        time.sleep(0.5)
    delete_cached_html(url.replace(" ", "%20"))
    soup = BeautifulSoup(html, "html.parser")
    if not soup:
        return
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
    skipped = 0
    for row in soup.select('tr'):
        name_cell = row.select_one('td.coll-1.name')
        if not name_cell:
            continue
 
        link_el = name_cell.select_one('a[href^="/torrent/"]')
        if not link_el:
            continue
        
        title = None
        try:
            title = link_el.get_text(strip=True)
        except Exception as e:
            skipped += 1
        link = None
        try:
            link = urljoin(url, str(link_el['href']))
        except:
            skipped += 1
        
        seeds_el = None
        leeches_el = None
        date_el = None
        size_el = None
        user_cell = None
        try:
            seeds_el = row.select_one('td.coll-2.seeds')
            leeches_el = row.select_one('td.coll-3.leeches')
            date_el = row.select_one('td.coll-date')
            size_el = row.select_one('td.coll-4.size')
            user_cell = row.select_one('td.coll-5')
        except:
            skipped += 1
 
        seeds = seeds_el.get_text(strip=True) if seeds_el else '0'
        leeches = leeches_el.get_text(strip=True) if leeches_el else '0'
        date = date_el.get_text(strip=True) if date_el else 'NULL'
 
        size = next(size_el.stripped_strings, 'NULL') if size_el else 'NULL'
 
        user_el = user_cell.select_one('a') if user_cell else None
        user = user_el.get_text(strip=True) if user_el else 'NULL'
 
        # badge = livello utente (vip/uploader/user), utile per valutare l'affidabilità del torrent
        user_classes = user_cell.get('class') if user_cell else []
        if user_classes and 'vip' in user_classes:
            badge = f'VIP - {user}' 
        elif user_classes and 'uploader' in user_classes:
            badge = f'Uploader - {user}' 
        else:
            badge = f'User - {user}' 
 
        description = f"{seeds} seeds - {leeches} leeches - {size} - {date} - by {user}"
 
        results['titles'].append(title or 'NULL')
        results['links'].append(link or 'NULL')
        results['images'].append('NULL')
        results['descriptions'].append(description)
        results['badges'].append(badge)
    
    if skipped != 0:
        return results, Error.from_code(ErrorCode.PARTIAL_PARSE_FAILED, origin=MODULE_INFO['id'], msg=f"Failed to parse {skipped} elements")
    return results, None

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('pokemon', MODULE_INFO['base_url'])
    print(res)