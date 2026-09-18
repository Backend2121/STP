# STP
A python based modular websites scraper with a webUI built with NiceGUI

## Features
* WebUI 
* Modular websites
* Extendable through extensions
* Automatic updates

## Requirements
* Python 3.14

# Installing
## Downloading
```bash
git clone https://github.com/Backend2121/STP.git
cd STP
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

# Setting up

## Core logic
*Module = Scraper*
*Extension = Feature*

## Modules
Every module must be put inside `STP/modules/` with the file name terminating in `_Module.py` and must provide:

* `getModuleInfo()`: returns metadata of the module
* `getLinks(query, base_url)`: searches for query and returns results/errors

## Extensions
Every extension must be put inside `STP/extensions/` with the file name terminating in `_Extension.py` and must provide:
* `getExtensionInfo()`: returns metadata of the extension

## Configuring .env
Rename .env.example to .env and configure it
```bash
mv .env.example .env
```

# Starting
```bash
python3 main.py
```

On first launch a `secret.txt` will be generated used to encrypt user sessions, *NEVER SHARE THIS FILE*

Web interface will be available at `http://localhost:8080`

# Updating
STP is capable of auto updates using this repo (main) as the source for updates
The webpage `/update` checks the local version against the remote version and downloads the remote version if newer

# Logging
STP logs to a new file each time it gets started, useful for debugging purposes and to keep track of what STP is doing

# Contributions
Very welcome!
Just follow the current structure and make a pull request!

# License
AGPLv3 https://www.gnu.org/licenses/agpl-3.0.html