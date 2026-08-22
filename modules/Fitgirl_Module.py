import requests
from bs4 import BeautifulSoup

MODULE_INFO = {
    'id': 'fitgirl',
    'display_name': 'Fitgirl',
    'base_url': 'https://fitgirl-repacks.site/?s=',
    'enabled': True,
    'version': '1.0.0',
    'icon': 'sports_esports',
    'color': '#1e88e5',
    'timeout': 10,
    'rate_limit_seconds': 1.0,
    'direct_link': False
}

xpath = "/html/body/div[2]/main/div/div/div[6]"

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
}

def getSoup(website: str) -> BeautifulSoup:
    """Given an url, return the soup of it using requests"""
    r = requests.get(url=website, headers=headers)
    if r.status_code != 200:
        raise RuntimeError(f"Status code for {website} is {r.status_code}")
    soup = BeautifulSoup(r.content, "html.parser")
    return soup

def getLinks(search, url):
    url += search
    soup = getSoup(url)
    game_articles = soup.find_all('article')
    results = {"titles": [], "links": [], "images": [], "descriptions": []}
    for article in game_articles:
        link = article.select_one("header h1 a")
        desc = article.select_one("div p")
        if link:
            results["titles"].append(link.get_text() or 'NULL')
            results["links"].append(link.get('href') or 'NULL')
        else:
            results["titles"].append('NULL')
            results["links"].append('NULL')
        results["images"].append('NULL')
        if desc:
            results["descriptions"].append(desc.get_text() or 'NULL')
        else:
            results["descriptions"].append('NULL')
    print(results)
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('dishonored', "https://fitgirl-repacks.site/?s=")
    print(res)