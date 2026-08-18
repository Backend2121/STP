import requests
from bs4 import BeautifulSoup

MODULE_INFO = {
    'id': 'ankergames2',
    'display_name': 'AnkerGames2',
    'base_url': 'https://ankergames.net/search/',
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
    games = soup.select("div.grid:nth-child(6)")
    results = {"titles": [], "links": [], "images": [], "descriptions": []}
    for game in games:
        for article in game.find_all("article"):
            results['titles'].append(article.get('title') or 'NULL')
            results['descriptions'].append(article.get('description') or 'NULL')
            results['images'].append(article.get('image') or 'NULL')
            link = article.find_all('div')[0].find_all('a')[0]
            results['links'].append(link.get('href') or 'NULL')
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('dishonored', "https://ankergames.net/search/")
    print(res)