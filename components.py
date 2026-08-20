import asyncio
from typing import Literal
from nicegui import Client, ui, app, run, events
import utils

class Header(ui.element):
    def __init__(self, tag: str | None = None, *, _client: Client | None = None, dark) -> None:
        super().__init__(tag, _client=_client)
        with ui.header().classes('items-center justify-between'):
                ui.label('Simple Things Provider').classes('text-xl cursor-pointer').on('click', lambda: ui.navigate.to('/'))
                with ui.row(align_items='center'):
                    ui.button('toggle', icon='dark_mode', on_click=dark.toggle)
                    ui.button(on_click=lambda: right_drawer.toggle(), icon='menu').props('flat color=white')

        with ui.right_drawer(fixed=False).props('bordered') as right_drawer:
            with ui.list().classes('w-full'):
                with ui.item(on_click=lambda: ui.navigate.to('/')).classes('cursor-pointer'):
                    with ui.item_section().props('avatar'):
                        ui.icon('home')
                    with ui.item_section():
                        ui.item_label('Home')
                with ui.item(on_click=lambda: ui.navigate.to('/settings')).classes('cursor-pointer'):
                    with ui.item_section().props('avatar'):
                        ui.icon('settings')
                    with ui.item_section():
                        ui.item_label('Settings')

class SearchBar(ui.column):
    def __init__(self, *, wrap: bool = False, align_items: None | Literal['start'] | Literal['end'] | Literal['center'] | Literal['baseline'] | Literal['stretch'] = None) -> None:
        super().__init__(wrap=wrap, align_items=align_items)
        with self.classes('w-full '):
            with ui.card().classes('w-[85%]'):
                    with ui.row(align_items='center').classes('w-full justify-between'):
                        self.search = ui.input('Search').classes('flex-3')
                        ui.button("Search", icon='search', on_click=lambda: self.get_links(self.search.value)).classes('flex-1')
    
    async def get_links(self, query: str | None) -> None:
        """Call getLinks on every currently active module and store results.
        
        Iterates over the modules currently selected/enabled, invokes their
        getLinks method, and writes the combined output to
        app.storage.user['search_results'].
        
        Args:
            query: The search term to pass to each module.
        
        Returns:
            None. Results are stored as a side effect in
            app.storage.user['search_results'].
        
        Raises:
            AttributeError: If a module does not expose a getLinks callable.
        """
        if query == None or query == "":
            ui.notify('Search bar is empty!', type='warning')
            return
        app.storage.user['search_results'] = {}
        selected_modules = app.storage.user['selected_modules']
        print(f"Selected modules: {selected_modules}")
        SearchResults.refresh()
        mods = utils.getModulesRefs()
        full_res = {"titles": [], "links": [], "images": [], "descriptions": [], "origin": []}
        for selected_module in selected_modules:
            for mod in mods:
                if selected_module == mod['id']:
                    with ui.row(align_items='center').classes('w-full justify-center') as row:
                        ui.spinner(size='lg')
                        ui.label('Loading...').classes('text-2xl font-bold')
                    try:
                        res = await asyncio.wait_for(run.cpu_bound(mod['mod'].getLinks, query, mod['base_url']), timeout=mod['timeout'])
                        row.clear()
                    except asyncio.TimeoutError:
                        row.clear()
                        ui.notify(f"Timeout for {mod['id']}",type='negative')
                        continue
                    if res:
                        full_res['titles'].append(res['titles'])
                        full_res['links'].append(res['links'])
                        full_res['images'].append(res['images'])
                        full_res['descriptions'].append(res['descriptions'])
                        full_res['origin'].append(mod['display_name'])
        app.storage.user['search_results'] = full_res
        SearchResults.refresh()

@ui.refreshable
class SearchResults(ui.grid):
    def __init__(self, *, rows: int | str | None = None, columns: int | str | None = None) -> None:
        super().__init__(rows=rows, columns=columns)
        self.classes('w-full grid-cols-1 sm:grid-cols-3 lg:grid-cols-5')
        try:
            if (len(app.storage.user['search_results']['titles'][0]) != 0):
                with self:
                    for i in range(0, len(app.storage.user['search_results']['titles'])):
                        titles = app.storage.user['search_results']['titles'][i]
                        descriptions = app.storage.user['search_results']['descriptions'][i]
                        images = app.storage.user['search_results']['images'][i]
                        links = app.storage.user['search_results']['links'][i]
                        origin = app.storage.user['search_results']['origin'][i]
                        for k,v in enumerate(titles):
                            with ui.card():
                                with ui.row(align_items='center').classes('w-full justify-between'):
                                    ui.label(text=v).classes('text-xl')
                                    ui.badge(text=origin).classes("py-2 text-center")
                                with ui.link(target=links[k], new_tab=True).classes('w-full h-full'):
                                    ui.image(source=images[k]).classes('object-scale-down')
                                    if (descriptions[k] != 'NULL'):
                                        ui.label(text=descriptions[k])
            else:
                with ui.label(text="No results").classes("w-full text-center text-2xl font-bold"):
                    pass
        except:
            pass