import time
from types import CoroutineType
from typing import Any

import requests
import asyncio
import utils
from nicegui import ui, app, run
from components import Header

EXTENSION_INFO = {
    'id': 'website_status_checker',
    'display_name': 'Website status checker',
    'base_url': '/website_status_checker',
    'enabled': True,
    'version': '1.0.0',
    'internal_page': False,
    'requires_extension': False,
    'icon': 'domain',
    'color': '#1e88e5',
    'timeout': 10,
    'rate_limit_seconds': 1.0,
    'direct_link': False
}

STATUS_TEXT = {
    200: 'OK', 301: 'Moved', 302: 'Found', 403: 'Forbidden', 404: 'Not Found',
    429: 'Rate Limited', 500: 'Server Error', 502: 'Bad Gateway',
    503: 'Unavailable/Anti-bot', 504: 'Gateway Timeout', 513: 'Unknown (513)',
    9001: 'SSLError -> Are you sure you are using a VPN?'
}

headers = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X x.y; rv:10.0) Gecko/20100101 Firefox/10.0',
}

results: dict[str, str] = {}

def pingWebsite(url: str, timeout: float) -> str:
    # Real pinger
    time.sleep(5)
    try:
        r = requests.get(url=url, timeout=timeout, headers=headers)
        return str(r.status_code)
    except Exception as e:
        if isinstance(e, requests.exceptions.SSLError):
            # Custom error code 9001 -> No VPN error
            return str(9001)
        return str(e)
 
async def ping_with_timeout(metadata: dict):
    # Pinger helper funciton, starts the thread
    # Can be removed, but it lets me have a timeout exception
    id = metadata['id']
    timeout = metadata.get('timeout', 10)
    try:
        res = await asyncio.wait_for(
            run.io_bound(pingWebsite, metadata['website'], timeout), timeout=timeout + 1
        )
        if res:
            results[id] = res
        else:
            results[id] = "NULL"
    except asyncio.TimeoutError:
        results[id] = 'Timeout'
    pingResults.refresh()
 
@ui.page(EXTENSION_INFO['base_url'])
async def extensionPage():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')
    Header(dark=dark, subPageText=EXTENSION_INFO['display_name'])
    modules_metadata = utils.getModulesMetadata()
    for m in modules_metadata:
        results[m['id']] = 'Loading'
    # Inner loop to start the pinger helper functions
    with ui.element().classes('w-full flex align-center justify-center items-center'):
        pingResults()
    # Epic function to wait for the ui to be ready before awaiting long shit
    await ui.context.client.connected()
    await asyncio.gather(*(ping_with_timeout(m) for m in modules_metadata))

@ui.refreshable
def pingResults():
    global results
    with ui.card().classes("min-w-1/2"):
        for k,v in results.items():
            if v == "Loading":
                with ui.row():
                    ui.label(text=f'{k}:').classes("font-bold")
                    ui.spinner(size='sm')
                    ui.label(text=" Loading...")
            else:
                with ui.row():
                        ui.label(text=f'{k}:').classes("font-bold")
                        if v.isnumeric():
                            ui.label(text=f'{v} {STATUS_TEXT[int(v)]}').classes(classifySeverity(v))

def classifySeverity(status_code: str) -> str:
    code = 0
    try:
        code = int(status_code)
    except:
        return ""
    if 200 <= code < 300:
        return 'bg-green-100 text-green-700 dark:bg-green-900 dark:text-green-300'
    elif 300 <= code < 400 or (400 <= code < 500 and code != 403):
        return 'bg-orange-100 text-orange-700 dark:bg-orange-900 dark:text-orange-300'
    else:
        return 'bg-red-100 text-red-700 dark:bg-red-900 dark:text-red-300'

def getExtensionInfo():
    return EXTENSION_INFO