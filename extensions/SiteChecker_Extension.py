from nicegui import ui, app
from components import Header


@ui.page('/SiteChecker')
def extensionPage():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')
    Header(dark=dark)
    with ui.label("SiteCheker"):
        pass