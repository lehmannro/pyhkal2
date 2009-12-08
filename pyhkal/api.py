# encoding: utf-8

import inspect
from distutils.version import LooseVersion
import pyhkal.shopping

def hi(**meta):
    """
    """
    mod = inspect.currentframe().f_back.f_globals
    if 'depends' in meta:
        for dependency in meta['depends']:
            dep = LooseVersion(dependency).version[0]
            mod[dep] = pyhkal.shopping.buy(dep)
    mod['NAME'] = meta['name']
    mod['__metadata__'] = meta #+ stack manipulation :-)

def hook(*event):
    return lambda f:f

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
