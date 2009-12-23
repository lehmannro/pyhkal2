# encoding: utf-8

import inspect
from distutils.version import LooseVersion
import pyhkal.davenport
import pyhkal.engine
import pyhkal.fred
import pyhkal.shopping

api = {}
def expose(item_or_name, item=None):
    """
    >>> expose(obj) # requires obj to have __name__ attribute
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

@expose
def send(message, dest=None):
    dispatch_event('send', message)

expose(pyhkal.davenport.remember)
expose(pyhkal.engine.dispatch_command)
expose("thread", pyhkal.fred.threaded)
