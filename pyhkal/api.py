# encoding: utf-8

import inspect
from distutils.version import LooseVersion
from twisted.application.service import Service
import pyhkal.davenport
import pyhkal.engine
import pyhkal.fred
import pyhkal.shopping

api = {}
def expose(item_or_name, item=None):
    """
    >>> expose(obj)
    >>> @expose
    ... def func(): pass
    ...
    >>> expose("name", obj)
    """
    if item:
        api[item_or_name] = item
    else:
        api[item_or_name.__name__] = item_or_name

@expose
def hi(**meta):
    """
    >>> hi(
    ...     version = "1.0",
    ...     depends = [
    ...         "modname",
    ...     ],
    ... )

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
    def deco(func):
        pyhkal.engine.add_listener(event, func)
        return func
    return deco

@expose
def register(func):
    name = func.__name__
    pyhkal.engine.add_command(name, func)
    return func

expose("twist", pyhkal.engine.add_service)

@expose
def send(message, dest=None):
    dispatch_event('send', message)

expose(pyhkal.davenport.remember)
expose(pyhkal.engine.dispatch_command)
expose("thread", pyhkal.fred.threaded)
