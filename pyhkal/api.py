# encoding: utf-8

import functools
import inspect
import os.path
from distutils.version import LooseVersion
import pyhkal.shopping
import pyhkal.engine

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

def hook(event, *args):
    def wrapper(f):
        pyhkal.engine.add_listener(event, f)
        return f
    return wrapper

def thread(func):
    return func

def register(command):
    return lambda f:f
    name = function.__name__
    if name in commands:
        raise ModuleError("duplicate namespace")
    commands[name] == function
    return function

def send(message, dest=None):
    """dest ist standardmäßig `origin` der vorher ausgeführten Funktion
    """
    for t in hooks['send'].values():
        t(message, dest)
