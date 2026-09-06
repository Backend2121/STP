import requests
from bs4 import BeautifulSoup
from nicegui import ui

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

def internalPage(selectedUrl: str):
    """Function used to display a custom page (eg. nested links) called after selecting a result from the main page"""
    soup = getSoup(selectedUrl)
    if not soup: return
    entry_content = soup.select_one("div.entry-content")
    if not entry_content: return
    title = entry_content.select_one("h3 strong")
    if not title: return
    img = entry_content.select_one("p a img")
    if not img: return
    infos = entry_content.select_one("p")
    if not infos: return
    li_elements = entry_content.select("ul li")
    if not li_elements: return
    links = []
    for li in li_elements:
        if len(li.select("a")) > 0:
            l = li.select_one("a")
            if not l: continue
            links.append(l)
    
    with ui.dialog() as dialog:
        with ui.card().classes("w-[80%] h-[80%] relative"):
            with ui.card().classes('sticky top-0 right-0 z-10 w-full flex-row justify-end gap-1 ml-auto'):
                ui.button(icon='close', on_click=dialog.close).props('flat round dense')
                ui.button(icon='open_in_new', on_click=lambda: ui.navigate.to(selectedUrl, new_tab=True)).props('flat round dense')
            with ui.column():
                ui.label(text=title.text).classes("w-full text-center text-2xl")
                ui.image(source=img.get('src')).classes('object-scale-down')
                ui.label(text="INFO").classes("w-full text-center text-xl")
                ui.label(text=infos.text)
                ui.label(text="LINKS").classes("w-full text-center text-xl")
                for link in links:
                    ui.link(text=link.text, target=link.get('href'))
    dialog.open()

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
    if not soup: return
    game_articles = soup.find_all('article')
    results = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": []}
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
    return results

def getModuleInfo():
    return MODULE_INFO

if __name__ == '__main__':
    res = getLinks('dishonored', "https://fitgirl-repacks.site/?s=")
    print(res)