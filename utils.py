import importlib

loaded_modules = []
loaded_modules_metadata = []

def loadModules(modules: list):
    global loaded_modules
    global loaded_modules_metadata
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