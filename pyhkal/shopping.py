#!/usr/bin/env python

"""Programming Is Hard, Let's Go Shopping!

"""

import imp
import os.path
import pkgutil
import sys
import pyhkal.api

SHOPPING_MALL = "contrib"

class OutOfStock(ImportError): pass

class ShoppingMall(object):
    @staticmethod
    def get_paths():
        curdir = os.path.dirname(__file__)
        #+ safeguard jail against ../
        reldir = lambda *d: os.path.abspath(os.path.join(curdir, *d))
        yield reldir(SHOPPING_MALL)
        yield reldir("..", SHOPPING_MALL)
        #+ try remember("include")
        #+ try $PYHKALPATH?
    def find_module(self, fullname, path=None):
        if fullname.startswith('pyhkal:'):
            return self
    def load_module(self, fullname):
        #+ handle failure during module loading (should not happen but better
        #  safe than sorry). this might be tricky as we'd need to rollback
        #  all changes to pyhkal.engine
        name = fullname[len('pyhkal:'):]
        self.loader = loader =  pkgutil.ImpLoader(
                fullname, *imp.find_module(name, list(self.get_paths())))
        mod = sys.modules.setdefault(fullname, imp.new_module(name))
        mod.__loader__ = self
        mod.__dict__.update(pyhkal.api.__dict__)
        mod.__dict__.update(__name__=name)
        exec loader.get_code() in mod.__dict__
        return mod

sys.meta_path.append(ShoppingMall())

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    namespace = dict(__module__=what)
    namespace.update(pyhkal.api.__dict__)
    mod = __import__('pyhkal:%s' % what, {}, namespace)
    mod.__name__ += '-' + mod.__metadata__['version']
    return mod

def revoke(what):
    pass
#    for command, func in commands.items():
#        if func.__file__ == mod:
#            del commands[command]
