# STP
A python based modular websites scraper with a webUI built with NiceGUI

## Features
* WebUI 
* Modular websites
* Extendable through extensions
* Automatic updates

## Requirements
* Python 3.10+ (3.14 recommended) https://www.python.org/downloads/
  The installer below sets it up for you where it can (winget on Windows, Homebrew on macOS)

# Installing
## Downloading
Download the latest (pre)release from https://github.com/Backend2121/STP/releases

### Or
```bash
git clone https://github.com/Backend2121/STP.git
```

## Quick install
Extract the downloaded `.zip`, open the extracted folder and run the installer for your OS.
It finds (or installs) Python, creates the `venv`, installs the requirements and creates your `.env`

| OS | Installer | Start STP later with |
|---|---|---|
| Windows | Double-click `install.bat` | `start.bat` |
| macOS | Double-click `install.command` | `start.command` |
| Linux | `bash install.sh` in the extracted folder | `bash start.sh` |

At the end the installer asks if you want to start STP right away

* **Windows:** if a "Security Warning" appears for the downloaded file, choose **Run**
* **macOS:** the first time, right-click `install.command` -> **Open** -> **Open** (Gatekeeper blocks downloaded scripts on a double-click). If it says the file is not executable, run `bash install.sh` in Terminal instead
* **Linux:** if Python 3.10+ is missing, the installer prints the package manager command to run (it never uses `sudo` by itself)

Run `install.bat --unattended` / `bash install.sh --unattended` to skip the prompts

## Manual install
Extract the `.zip`, open the extracted folder in a terminal/cmd and run the following:

### (if `python3` is not found use `python` for the rest of the guide)

```bash
python3 -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Configuring .env
Rename `.env.example` to `.env` and configure it
```bash
mv .env.example .env          # Windows: ren .env.example .env
```

## Installing STP's web extension

STP Extension captures a page's full HTML once it has finished loading and sends it to `/api/eb` API
The extension only captures pages whose URL contains `#stp-capture`

- Unzip `STP_WE.zip`

### Firefox

1. Open `about:debugging#/runtime/this-firefox`
2. Click **Load Temporary Add-on…**
3. Select the `manifest.json` file in the project's root folder

Firefox unloads temporary add-ons when it closes, so repeat these steps after a restart

### Chrome

1. Open `chrome://extensions`
2. Turn on **Developer mode** (top-right)
3. Click **Load unpacked** and select the `dist/chrome` folder

### Configure

Set the **API host** (`ip:port`) in the extension's settings
It defaults to `127.0.0.1:8080`, and HTML pages are sent to `http://<ip:port>/api/eb`

- **Firefox:** `about:addons` → **STP Extension** → **Preferences**
- **Chrome:** `chrome://extensions` → **Details** on the extension → **Extension options**

# Starting
Use the launcher created for your OS: `start.bat` (Windows), `start.command` (macOS) or `bash start.sh` (Linux)

Or, with a manual install (venv activated):
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

# License
AGPLv3 https://www.gnu.org/licenses/agpl-3.0.html