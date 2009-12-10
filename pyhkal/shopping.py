#!/usr/bin/env python

"""Programming Is Hard, Let's Go Shopping!

"""

import os.path
import pyhkal.api

SHOPPING_MALL = os.path.abspath(os.path.join(os.path.dirname(__file__),
    "contrib"))
_modules = set()

class OutOfStock(ImportError): pass

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    elif what in _modules:
        return
    #+ safeguard jail against ../
    #+ try ../contrib?
    #+ try remember("include")
    #+ try $PYHKALPATH?
    path = os.path.join(SHOPPING_MALL, what+".py")
    if not os.path.isfile(path):
        raise OutOfStock(what)
    execfile(path, pyhkal.api.__dict__, {'NAME': what})
    _modules.add(what)

def revoke(what):
    pass
#    for command, func in commands.items():
#        if func.__file__ == mod:
#            del commands[command]
