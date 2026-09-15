from enum import IntEnum
import importlib
import os
from typing import Literal, Optional
from urllib.parse import quote
from dataclasses import dataclass, field
import logging
import sys
from datetime import datetime
from pathlib import Path
import uuid
import requests
import re

VERSION = '1.0.0'

_update_available: bool = False

loaded_modules = []
loaded_modules_metadata = []

loaded_extensions = []
loaded_extensions_metadata = []

_html_cache: dict[str, str] = {}

_logger = None

class ErrorCode(IntEnum):
    """Enum for error codes -> mapped by ERROR_REGISTRY"""
    WEBSITE_PARSE_FAILED = 100
    CORE_PARSING_FAILED = 101
    EMPTY_RESPONSE = 102
    PARTIAL_PARSE_FAILED = 103
    INVALID_MODULE = 104
    TIMEOUT = 105
    FORBIDDEN = 106

ERROR_REGISTRY: dict[ErrorCode, tuple[int, str]] = {
    ErrorCode.WEBSITE_PARSE_FAILED: (3, "Failed to fetch the page"),
    ErrorCode.CORE_PARSING_FAILED: (3, "Failed to parse main content"),
    ErrorCode.EMPTY_RESPONSE: (3, "The server returned an empty response"),
    ErrorCode.PARTIAL_PARSE_FAILED: (2, "Some results could not be parsed"),
    ErrorCode.INVALID_MODULE: (3, "The requested module does not exist"),
    ErrorCode.TIMEOUT: (2, "The request timed out"),
    ErrorCode.FORBIDDEN: (3, "Access forbidden - VPN may be required"),
}

@dataclass
class Error:
    """
    1 = Info
    2 = Warning
    3 = Error
    4 = Critical
    """
    code: int
    origin: str
    severity: int = 1
    alert_type: Literal[
               'positive',
               'negative',
               'warning',
               'info',
               'ongoing',
           ] = 'info'
    msg: str = ""
    exception: str = ""
    @classmethod
    def from_code(cls, code: ErrorCode, origin: str, exception: Exception | None = None, msg: Optional[str] = None) -> "Error":
        # TODO Add logger call here
        severity, default_msg = ERROR_REGISTRY[code]
        alert_type = 'info'
        if severity == 1: alert_type = 'info'
        if severity == 2: alert_type = 'warning'
        if severity == 3: alert_type = 'negative'
        if severity == 4: alert_type = 'negative'
        return cls(code=code, origin=origin, severity=severity, alert_type=alert_type, msg=msg or default_msg, exception=str(exception))

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
    source_url: Optional[str] = None

def listAllPythonFiles():
    cwd = os.getcwd()
    python_files = []
    scannable_subdirs = [cwd + '/extensions', cwd + '/modules', cwd]
    for subdir in scannable_subdirs:
        files = os.listdir(subdir)
        for file in files:
            if file.endswith(".py"):
                relativeSubdir = subdir.split('/')[-1]
                # Dodge the STP main folder and append only the base file name
                if relativeSubdir == 'STP':
                    python_files.append(file)
                else:
                    python_files.append(relativeSubdir + '/' + file)

    return python_files

def getUpdateAvailable():
    global _update_available
    return _update_available

def setUpdateAvailable(val: bool):
    global _update_available
    _update_available = val

def updateAvailable(remote_major, local_major, remote_minor, local_minor, remote_bugfix, local_bugfix) -> int:
    if remote_major > local_major:
        return 1
    if remote_minor > local_minor:
        return 2
    if remote_bugfix > local_bugfix:
        return 3
    return 0

def checkUpdates():
    files = listAllPythonFiles()
    log = getLogger()
    log.info("[Updater] Checking for updates")
    for file in files:
        r = requests.get(f"https://raw.githubusercontent.com/Backend2121/STP/main/{file}")
        remote_major = None
        local_major = None
        remote_minor = None
        local_minor = None
        remote_bugfix = None
        local_bugfix = None
        if r.status_code == 200:
            # Locate the file VERSION "variable"
            # Locates in the first group the major, minor, bugfix numbers
            remote_matches = re.findall(r"(?:VERSION|'version')\s?(?:=|:)\s?'(\d+.\d+.\d+)'", r.text)
            if len(remote_matches) == 1:
                remote_major, remote_minor, remote_bugfix = [ int(i) for i in remote_matches[0].split(".")]
            else:
                log.error("[Updater] Remote %s version undefined", file)
                continue
            # Read local file
            with open(os.getcwd() + "/" + file, "r") as f:
                local_matches = re.findall(r"(?:VERSION|'version')\s?(?:=|:)\s?'(\d+.\d+.\d+)'", f.read())
                if len(local_matches) == 1:
                    local_major, local_minor, local_bugfix = [ int(i) for i in local_matches[0].split(".")]
                else:
                    log.error("[Updater] Local %s version undefined", file)
                    continue
        res = updateAvailable(remote_major, local_major, remote_minor, local_minor, remote_bugfix, local_bugfix)
        if res == 1:
            log.warning("[Updater] Major update for %s is available", file)
            setUpdateAvailable(True)
        if res == 2:
            log.warning("[Updater] Minor update for %s is available", file)
            setUpdateAvailable(True)
        if res == 3:
            log.warning("[Updater] Bugfix update for %s is available", file)
            setUpdateAvailable(True)
    log.info("[Updater] Successfully checked for updates")

def getLogger(name="stp_logger", log_dir="logs", level=logging.DEBUG):
    # Singleton behaviour
    global _logger
    if _logger is not None:
        return _logger

    Path(log_dir).mkdir(exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = Path(log_dir) / f"{name}_{timestamp}.log"

    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.propagate = False

    fmt = logging.Formatter(
        "%(asctime)s [%(levelname)-8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(fmt)
    logger.addHandler(console_handler)

    _logger = logger
    return _logger

def getSecret() -> str:
    log = getLogger()
    secretPath = (Path(os.getcwd()) / "secret.txt")
    if not secretPath.exists():
        log.debug("Creating secret")
        secretPath.touch(exist_ok=True)
        secretPath.write_text(str(uuid.uuid4()))
        log.debug("Successfully created secret")
    log.debug("Loading secret")
    return secretPath.read_text()

def print_cached_html():
    print(_html_cache)

def get_cached_html(url: str) -> str | None:
    return _html_cache.get(url, None)

def cache_html(url: str, html: str) -> None:
    _html_cache[url] = html
    log = getLogger()
    log.info("Correctly received %s HTML from web extension", url)

def delete_cached_html(url: str) -> bool:
    removed = _html_cache.pop(url, '')
    log = getLogger()
    if removed == '':
        log.debug("Correctly received %s HTML from web extension", url)
        return False
    log.debug("Correctly removed %s key, value pair from _html_cache", url)
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
    
    log = getLogger()
    
    cwd = os.getcwd() + '/'
    modules_directory = cwd + 'modules'
    files_in_modules_directory = os.listdir(modules_directory)
    modules = []
    for file in files_in_modules_directory:
        if file.endswith("Module.py"):
            modules.append(file.replace('.py', ''))
    
    log.debug("Found %d module files in %s", len(modules), modules_directory)
    log.debug("Importing %d modules", len(modules))
    
    for module in modules:
        log.debug("Loading %s.py", module)
        mod = importlib.import_module(f'modules.{module}')
        log.debug("Successfully loaded %s.py", module)
        module_metadata = None
        try:
            module_metadata = mod.getModuleInfo()
            loaded_modules_metadata.append(module_metadata.copy())
        except Exception as e:
            log.exception("Unable to find getModuleInfo on %s.py", module)
            return

        if module_metadata:
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
    
    log = getLogger()
    
    cwd = os.getcwd() + '/'
    extensions_directory = cwd + 'extensions'
    files_in_extensions_directory = os.listdir(extensions_directory)
    extensions = []
    for file in files_in_extensions_directory:
        if file.endswith("Extension.py"):
            extensions.append(file.replace('.py', ''))
    
    log.debug("Found %d extension files in %s", len(extensions), extensions_directory)
    log.debug("Importing %d extensions", len(extensions))
    
    for extension in extensions:
        log.debug("Loading %s.py", extension)
        ext = importlib.import_module(f'extensions.{extension}')
        log.debug("Loaded %s.py", extension)
        extension_metadata = None
        try:
            extension_metadata = ext.getExtensionInfo()
            loaded_extensions_metadata.append(extension_metadata.copy())
        except Exception as e:
            log.exception("Unable to find getExtensionInfo on %s.py", extension)
        if extension_metadata:
            extension_metadata.update({'ext': ext})
            loaded_extensions.append(extension_metadata)
        
def getExtensionsMetadata() -> list[dict]:
    global loaded_extensions_metadata
    return loaded_extensions_metadata

def getExtensionsRefs() -> list[dict]:
    global loaded_extensions
    return loaded_extensions