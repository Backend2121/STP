from nicegui import ui, app
from components import SearchBar, SearchResults, Header
import utils

imported_modules = []

@ui.page('/settings')
def settings_page():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')
    modules = app.storage.user['modules']
    # Build a {key: value} dict for each module in modules
    options = {
        module['id']: f"{module['display_name']} - {module['version']}"
        for module in modules
    }

    if 'selected_modules' not in app.storage.user:
        app.storage.user['selected_modules'] = []

    Header(dark=dark)
    with ui.column().classes('w-full'):
        ui.select(options=options, multiple=True, label="Modules").classes('w-[50%]').props('use-chips').bind_value(app.storage.user, 'selected_modules')

@ui.page('/')
def home_page():
    dark = ui.dark_mode()
    dark.bind_value(app.storage.user, 'dark_mode')
    app.storage.user.setdefault('search_results', {})
    app.storage.user.setdefault('modules', [])
    app.storage.user.setdefault('selected_modules', {})
    app.storage.user['modules'] = utils.getModulesMetadata()

    Header(dark=dark)
    with SearchBar(align_items='center'):
        pass
    SearchResults()
    with ui.page_sticky(x_offset=18, y_offset=18):
            ui.button(icon='keyboard_arrow_up', on_click=lambda: ui.run_javascript('window.scrollTo({top:0, behavior:"smooth"})'))

def runGUI(modules: list[dict]):
    utils.loadModules(modules)
    ui.run(reload=True, storage_secret='UUID_GENERATE', title='Simple Things Provider',
           favicon='data:image/png;base64,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')
