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
        #+ do not neccessarily reset dunder attributes on reload
        #  (fullname in sys.modules)
        name = fullname[len('pyhkal:'):]
        self.loader = loader =  pkgutil.ImpLoader(
                fullname, *imp.find_module(name, list(self.get_paths())))
        mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
        mod.__loader__ = self
        mod.__dict__.update(pyhkal.api.api)
        mod.__name__ = fullname
        mod.__module__ = name
        exec loader.get_code() in mod.__dict__
        return mod

sys.meta_path.append(ShoppingMall())

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    mod = __import__('pyhkal:%s' % what)
    return mod

def renew(what):
    reload(sys.modules['pyhkal:%s' % what])

def revoke(what):
    del sys.modules['pyhkal:%s' % what]
