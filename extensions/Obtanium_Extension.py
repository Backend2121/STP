from nicegui import ui, app
from components import Header

EXTENSION_INFO = {
    'id': 'obtanium',
    'display_name': 'Obtanium',
    'base_url': '/obtanium',
    'enabled': True,
    'version': '1.0.0',
    'internal_page': False,
    'requires_extension': False,
    'icon': 'download',
    'color': '#1e88e5',
    'timeout': 10,
    'rate_limit_seconds': 1.0,
    'direct_link': False
}

@ui.page(EXTENSION_INFO['base_url'])
def extensionPage():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')
    Header(dark=dark, subPageText=EXTENSION_INFO['display_name'])
    with ui.label(EXTENSION_INFO['display_name']):
        pass

def getExtensionInfo():
    return EXTENSION_INFO