#!/usr/bin/env python

"""Programming Is Hard, Let's Go Shopping!

"""

import imp
import os.path
import pkgutil
import sys

SHOPPING_MALL = "contrib"

class OutOfStock(ImportError): pass

class ShoppingMall(object):
    def __init__(self, service):
        self.service = service

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
        #+ do not neccessarily reset dunder attributes on reload
        #  (fullname in sys.modules)
        name = fullname[len('pyhkal:'):]
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        loader = pkgutil.ImpLoader(
            fullname, *imp.find_module(name, list(self.get_paths())))
        from pyhkal.api import apply
        api = apply(self.service)
        mod.__mod__ = name
        mod.__dict__.update(api)
        mod.__loader__ = self
        mod.__file__ = loader.get_filename()
        exec loader.get_code() in mod.__dict__
        for dep in getattr(mod, '__requires__', []):
            mod.__dict__[dep] = buy(dep)
        return mod

def checkout(customer):
    mall = ShoppingMall(customer)
    sys.meta_path.append(mall)
    return mall

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    mod = __import__('pyhkal:%s' % what)
    return mod

def renew(what):
    reload(sys.modules['pyhkal:%s' % what])

def revoke(what):
    del sys.modules['pyhkal:%s' % what]
