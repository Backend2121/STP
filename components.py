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
        full_res = {"titles": [], "links": [], "images": [], "descriptions": [], "badges": [], "origin": [], "modId": []}
        for selected_module in selected_modules:
            for mod in mods:
                if selected_module == mod['id']:
                    with ui.row(align_items='center').classes('w-full justify-center') as row:
                        ui.spinner(size='lg')
                        ui.label('Loading...').classes('text-2xl font-bold')
                    try:
                        if mod['requires_extension'] == True:
                            with ui.dialog() as dialog, ui.card():
                                ui.label("Do you want to open the module's target website to solve Cloudflare's challenge?\n (Required to fetch results)")
                                with ui.row():
                                    ui.button('Yes', on_click=lambda: dialog.submit('Yes'))
                                    ui.button('No', on_click=lambda: dialog.submit('No'))
                            if await dialog == 'Yes':
                                link = mod['mod'].build_link(query)
                                ui.navigate.to(link + "#stp-capture", new_tab=True)
                            else:
                                # If the user chooses 'NO' the module is simply skipped
                                continue
                        res = await asyncio.wait_for(run.io_bound(mod['mod'].getLinks, query, mod['base_url']), timeout=mod['timeout'])
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
                        full_res['badges'].append(res['badges'])
                        full_res['origin'].append(mod['display_name'])
                        full_res['modId'].append(mod['id'])
        app.storage.user['search_results'] = full_res
        SearchResults.refresh()

@ui.refreshable
class SearchResults(ui.grid):
    def __init__(self, *, rows: int | str | None = None, columns: int | str | None = None) -> None:
        super().__init__(rows=rows, columns=columns)
        self.classes('w-full grid-cols-1 sm:grid-cols-3 lg:grid-cols-5')
        try:
            if utils.has_nested_value(app.storage.user['search_results']):
                with self:
                    for i in range(0, len(app.storage.user['search_results']['titles'])):
                        titles = app.storage.user['search_results']['titles'][i]
                        descriptions = app.storage.user['search_results']['descriptions'][i]
                        images = app.storage.user['search_results']['images'][i]
                        links = app.storage.user['search_results']['links'][i]
                        badges = app.storage.user['search_results']['badges'][i]
                        origin = app.storage.user['search_results']['origin'][i]
                        modId = app.storage.user['search_results']['modId'][i]
                        mod = utils.getModuleById(modId)
                        for x in range(0, len(titles)):
                            with ui.card():
                                with ui.row(align_items='center').classes('w-full justify-between'):
                                    ui.label(text=titles[x]).classes('text-xl')
                                    ui.badge(text=origin).classes("py-2 text-center")
                                    ui.badge(text=badges[x]).classes("py-2 text-center")
                                if mod and mod['internal_page'] == True:
                                    if images[x] != 'NULL':
                                        ui.image(source=images[x]).classes('object-scale-down')
                                    ui.button(text="Select link", on_click=lambda m=modId, t=links[x]: self.open_internal_page(str(m), t)).classes('w-full text-center')
                                else:
                                    with ui.link(target=links[x], new_tab=True).classes('w-full h-full'):
                                        if images[x] != 'NULL':
                                            ui.image(source=images[x]).classes('object-scale-down')
                                        if (descriptions[x] != 'NULL'):
                                            ui.label(text=descriptions[x])
            else:
                with ui.label(text="No results").classes("w-full text-center text-2xl font-bold"):
                    pass
        except Exception as e:
            print(e)
            pass
    
    async def open_internal_page(self, modId:str, target:str):
        mod = utils.getModuleById(modId)
        if mod and mod['internal_page'] == True:     
            info = None
            try:
                if mod['requires_extension']:
                    ui.navigate.to(target + "#stp-capture", new_tab=True)
                info = await asyncio.wait_for(run.io_bound(mod['mod'].internalPage, target), timeout=mod['timeout'])
            except asyncio.TimeoutError:
                ui.notify(f"Timeout for {mod['id']}",type='negative')
            if info and isinstance(info, utils.DownloadInfo):
                with ui.dialog() as dialog:
                    with ui.card().classes('w-[80%] h-[80%] relative overflow-y-auto p-0'):
            
                        # Header
                        with ui.card().classes(
                            'sticky top-0 right-0 z-10 w-full flex-row justify-end gap-1 m-0'
                        ):
                            ui.button(icon='close', on_click=dialog.close).props('flat round dense')
                            if info.source_url:
                                ui.button(
                                    icon='open_in_new',
                                    on_click=lambda: ui.navigate.to(str(info.source_url), new_tab=True),
                                ).props('flat round dense')
                        # The rest
                        with ui.column().classes('w-full p-4 gap-3 items-center'):
            
                            if info.image:
                                ui.image(info.image).classes('max-w-full max-h-64').props('fit=scale-down')
                            else:
                                ui.icon('image_not_supported', size='xl').classes('text-gray-400')
            
                            ui.label(info.title).classes('text-2xl font-bold text-center')
            
                            if info.description:
                                ui.label(info.description).classes('text-center text-gray-600')
            
                            if info.details:
                                with ui.grid(columns=2).classes('w-full max-w-md gap-x-4 gap-y-1'):
                                    for label, value in info.details.items():
                                        ui.label(label).classes('font-semibold text-right')
                                        ui.label(value)
            
                            if info.links:
                                with ui.row().classes('w-full flex-wrap justify-center gap-2 mt-2'):
                                    for link in info.links:
                                        ui.button(
                                            link.label,
                                            icon='download',
                                            on_click=lambda _, l=link: ui.navigate.to(l.url, new_tab=True),
                                        )
                dialog.open()