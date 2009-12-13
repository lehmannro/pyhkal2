# encoding: utf-8

import inspect
from distutils.version import LooseVersion
import pyhkal.shopping
import pyhkal.engine
import pyhkal.davenport

#+ expose only specially marked up items
api_keys = set()
def expose(item):
    api_keys.add(item)
    return item

@expose
def hi(**meta):
    """
    """
    frame = inspect.currentframe().f_back
    mod = frame.f_globals
    if 'depends' in meta:
        for dependency in meta['depends']:
            dep = LooseVersion(dependency).version[0]
            mod[dep] = pyhkal.shopping.buy(dep)
    mod['__metadata__'] = meta

@expose
def hook(event, *args):
    def wrapper(f):
        pyhkal.engine.add_listener(event, f)
        return f
    return wrapper

@expose
def thread(func):
    return func

@expose
def register(command):
    return lambda f:f
    name = function.__name__
    if name in commands:
        raise ModuleError("duplicate namespace")
    commands[name] == function
    return function

@expose
def send(message, dest=None):
    """dest ist standardmäßig `origin` der vorher ausgeführten Funktion
    """
    for t in hooks['send'].values():
        t(message, dest)

expose(pyhkal.davenport.remember)

api = dict((v.__name__, v) for v in api_keys)
