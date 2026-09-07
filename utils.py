import importlib
import os
from typing import Optional
from urllib.parse import quote
from dataclasses import dataclass, field

loaded_modules = []
loaded_modules_metadata = []

loaded_extensions = []
loaded_extensions_metadata = []

_html_cache: dict[str, str] = {}

@dataclass
class DownloadLink:
    label: str
    url: str

@dataclass
class DownloadInfo:
    title: str
    image: Optional[str] = None
    description: Optional[str] = None
    details: dict[str, str] = field(default_factory=dict)
    links: list[DownloadLink] = field(default_factory=list)
    source_url: Optional[str] = None  # pagina originale, per "open_in_new"

def print_cached_html():
    print(_html_cache)

def get_cached_html(url: str) -> str | None:
    return _html_cache.get(url, None)

def cache_html(url: str, html: str) -> None:
    _html_cache[url] = html
    # print_cached_html()

def delete_cached_html(url: str) -> bool:
    removed = _html_cache.pop(url, '')
    if removed == '':
        return False
    return True

def convert_to_html_string(query:str) -> str:
    return quote(query)

def has_nested_value(d: dict) -> bool:
    return any(
        item
        for lists in d.values()
        for sublist in lists
        for item in sublist
    )

def getModuleById(modId: str):
    mods = getModulesRefs()
    for mod in mods:
        if modId == mod['id']:
            return mod

def loadModules():
    global loaded_modules
    global loaded_modules_metadata
    
    cwd = os.getcwd() + '/'
    modules_directory = cwd + 'modules'
    files_in_modules_directory = os.listdir(modules_directory)
    modules = []
    for file in files_in_modules_directory:
        if 'Module.py' in file:
            modules.append(file.replace('.py', ''))
    
    for module in modules:
        mod = importlib.import_module(f'modules.{module}')
        module_metadata = mod.getModuleInfo()
        loaded_modules_metadata.append(module_metadata.copy())
        
        module_metadata.update({'mod': mod})
        loaded_modules.append(module_metadata)

def getModulesMetadata() -> list[dict]:
    global loaded_modules_metadata
    return loaded_modules_metadata

def getModulesRefs() -> list[dict]:
    global loaded_modules
    return loaded_modules

def loadExtensions():
    global loaded_extensions
    global loaded_extensions_metadata
    
    cwd = os.getcwd() + '/'
    extensions_directory = cwd + 'extensions'
    files_in_extensions_directory = os.listdir(extensions_directory)
    extensions = []
    for file in files_in_extensions_directory:
        if file.endswith("Extension.py"):
            extensions.append(file.replace('.py', ''))
    
    for extension in extensions:
        ext = importlib.import_module(f'extensions.{extension}')
        extension_metadata = ext.getExtensionInfo()
        loaded_extensions_metadata.append(extension_metadata.copy())
        
        extension_metadata.update({'ext': ext})
        loaded_extensions.append(extension_metadata)
        
def getExtensionsMetadata() -> list[dict]:
    global loaded_extensions_metadata
    return loaded_extensions_metadata

def getExtensionsRefs() -> list[dict]:
    global loaded_extensions
    return loaded_extensions