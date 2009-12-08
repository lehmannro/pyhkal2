#!/usr/bin/env python

"""Programming Is Hard, Let's Go Shopping!

"""

import os.path
import pyhkal.api

SHOPPING_MALL = os.path.abspath(os.path.join(os.path.dirname(__file__),
    "..", "contrib"))

def buy(what):
    if what == "love":
        raise SystemExit("Can't Buy Me Love")
    return execfile(os.path.join(SHOPPING_MALL, what+".py"),
        pyhkal.api.__dict__)

def revoke(what):
    pass
#    for command, func in commands.items():
#        if func.__file__ == mod:
#            del commands[command]
