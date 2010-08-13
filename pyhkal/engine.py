#!/usr/bin/env python
# encoding: utf-8

import collections
import weakref
from _weakrefset import WeakSet

try:
    import json
except ImportError:
    import simplejson
else:
    import sys
    sys.modules['simplejson'] = json

from pyhkal import davenport, shopping


listeners = collections.defaultdict(WeakSet)
#+ support subcommands
commands = weakref.WeakValueDictionary()
# dict of str -> (callback, dict of str -> (callback, dict ...))
application = None

def run(app):
    global application
    application = app
    sofa = davenport.Davenport() #XXX
    for mod in sofa.remember("modules"):
        shopping.buy(mod)
    dispatch_event("startup")

def add_service(service):
    service.setServiceParent(application)

def add_listener(event, listener):
    listeners[event].add(listener)

def dispatch_event(event, *args):
    for dispatcher in listeners[event]:
        dispatcher(*args)

def add_command(command, listener, parent=None):
    #+ support subcommands
    if command in commands:
        raise SystemError
    commands[command] = listener

def dispatch_command(origin, command, args):
    #+ subcommand dispatch
    #+ check for number of arguments
    if command in commands:
        commands[command](origin, args)
