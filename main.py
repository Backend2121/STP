import gui
import utils

VERSION = '1.0.0'

if __name__ in {"__main__", "__mp_main__"}:
    utils.checkUpdates()
    gui.runGUI()