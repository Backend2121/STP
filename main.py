import gui
import os

if __name__ in {"__main__", "__mp_main__"}:
    print("Enumerating modules")
    cwd = os.getcwd() + '/'
    modules_directory = cwd + 'modules'
    files_in_modules_directory = os.listdir(modules_directory)
    modules = []
    for file in files_in_modules_directory:
        if 'Module.py' in file:
            modules.append(file.replace('.py', ''))
    loaded_modules = []
    for module in modules:
        loaded_modules.append(module)
    gui.runGUI(loaded_modules)