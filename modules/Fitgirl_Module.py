import re

import requests
from bs4 import BeautifulSoup
from bs4.element import NavigableString
from utils import DownloadLink, DownloadInfo

MODULE_INFO = {
    'id': 'fitgirl',
    'display_name': 'Fitgirl',
    'base_url': 'https://fitgirl-repacks.site/?s=',
    'enabled': True,
    'version': '1.0.0',
    'internal_page': True,
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

DETAIL_LABELS = ['Genres/Tags', 'Company', 'Companies', 'Languages', 'Original Size', 'Repack Size']

def internalPage(selectedUrl: str):
    """Function used to display a custom page (eg. nested links) called after selecting a result from the main page"""
    soup = getSoup(selectedUrl)
    # Title
    if not soup: return
    first_h3 = soup.find('h3')
    strong = first_h3.find('strong') if first_h3 else None
    title = (strong or first_h3).get_text(' ', strip=True) if first_h3 else 'Unknown'
 
    # Image
    img_el = soup.find('img')
    image = img_el.get('src') if img_el else None
 
    # Details
    details: dict[str, str] = {}
    intro_p = first_h3.find_next('p') if first_h3 else None
    if intro_p:
        text = intro_p.get_text(' ', strip=True)
        pattern = '|'.join(re.escape(l) for l in DETAIL_LABELS)
        matches = list(re.finditer(rf'({pattern}):\s*', text))
        for i, m in enumerate(matches):
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            details[m.group(1)] = text[m.end():end].strip()
 
    # Descriptions
    description = None
    for title_div in soup.select('.su-spoiler-title'):
        if title_div.get_text(strip=True) == 'Game Description':
            content = title_div.find_next_sibling('div', class_='su-spoiler-content')
            if content:
                leading = next(
                    (c for c in content.contents if isinstance(c, NavigableString) and c.strip()), ''
                )
                description = leading.strip() or None
            break
 
    # Links
    links: list[DownloadLink] = []
    for h3 in soup.find_all('h3'):
        heading = h3.get_text(strip=True)
        if not heading.startswith('Download Mirrors'):
            continue
 
        suffix = heading.replace('Download Mirrors', '').strip('() ')
        ul = h3.find_next('ul')
        if not ul:
            continue
 
        for li in ul.find_all('li', recursive=False):
            for spoiler in li.select('div.su-spoiler'):
                spoiler.extract()
 
            anchors = li.find_all('a')
            if not anchors:
                continue
 
            label = anchors[0].get_text(strip=True)
            if anchors[0].get('href'):
                full_label = f'{label} ({suffix})' if suffix else label
                links.append(DownloadLink(full_label, str(anchors[0]['href'])))
 
            for a in anchors[1:]:
                if a.get_text(strip=True).lower() == 'magnet':
                    links.append(DownloadLink(f'{label} (Magnet)', str(a['href'])))
 
    return DownloadInfo(title, str(image), description, details, links, selectedUrl)

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
    soup = getSoup(url)
    if not soup:
        return
    game_articles = soup.find_all('article')
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
 
    for article in game_articles:
        link = article.select_one("header h1 a")
        desc = article.select_one("div.entry-summary p")
 
        if link:
            results["titles"].append(link.get_text(strip=True) or 'NULL')
            results["links"].append(link.get('href') or 'NULL')
        else:
            results["titles"].append('NULL')
            results["links"].append('NULL')
 
        results["images"].append('NULL')
 
        if desc:
            more_link = desc.select_one('a.more-link')
            if more_link:
                more_link.extract()
            results["descriptions"].append(desc.get_text(separator=' ', strip=True) or 'NULL')
        else:
            results["descriptions"].append('NULL')
 
        # bug originale: la chiave 'badges' esisteva nel dict ma non veniva
        # mai popolata nel loop -> liste di lunghezza diversa, indici disallineati
        tag_links = article.select('footer.entry-meta a[rel="tag"]')
        badge = ', '.join(a.get_text(strip=True) for a in tag_links) if tag_links else 'NULL'
        results["badges"].append(badge)
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('dishonored', "https://fitgirl-repacks.site/?s=")
    print(res)