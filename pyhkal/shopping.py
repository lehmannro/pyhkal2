#!/usr/bin/env python

"""Programming Is Hard, Let's Go Shopping!

"""

import imp
import os.path
import pkgutil
import runpy
import pyhkal.api

SHOPPING_MALL = os.path.abspath(os.path.join(os.path.dirname(__file__),
    "contrib"))
_modules = set()

class OutOfStock(ImportError): pass

class ShoppingMall(pkgutil.ImpImporter):
    def find_module(self, fullname, path=None):
        if fullname.startswith('pyhkal:'):
            name = fullname[len('pyhkal:'):]
            #+ safeguard jail against ../
            #+ try ../contrib?
            #+ try remember("include")
            #+ try $PYHKALPATH?
            path = os.path.join(SHOPPING_MALL, name+".py")
            if not os.path.isfile(path):
                return None
            #+ handle failure during module loading (should not happen but better
            #  safe than sorry). this might be tricky as we'd need to rollback
            #  all changes to pyhkal.engine
            return pkgutil.ImpLoader(
                fullname, open(path), path, (".py", 'r', imp.PY_SOURCE))
import sys
sys.meta_path.append(ShoppingMall())

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    elif what in _modules:
        return
    namespace = {'__module__': what}
    namespace.update(pyhkal.api.__dict__)
    namespace = runpy.run_module("pyhkal:%s" % what, namespace)
    _modules.add(what)
    namespace['__name__'] += "-" + namespace['__metadata__']['version']
    mod = imp.new_module("")
    mod.__dict__.update(namespace)
    return mod

def revoke(what):
    pass
#    for command, func in commands.items():
#        if func.__file__ == mod:
#            del commands[command]
