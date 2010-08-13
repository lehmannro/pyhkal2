#!/usr/bin/env python
# encoding: utf-8

import collections
import weakref
from _weakrefset import WeakSet
try: # inject json as simplejson
    import json
except ImportError:
    import simplejson
else:
    import sys
    sys.modules['simplejson'] = json

from twisted.application import service
from twisted.internet import reactor
from pyhkal import shopping
from pyhkal.davenport import Davenport

class Pyhkal(service.Service):
    def __init__(self, screwdriver):
        self.screwdriver = screwdriver

    def startService(self):
        #XXX reloadable
        db = self.screwdriver['database']
        self.davenport = Davenport(db['host'], 'pyhkal', db['username'],
                db['password'], db['port'])
        self.listeners = collections.defaultdict(WeakSet)
        self.commands = weakref.WeakValueDictionary()
        self.mall = shopping.checkout(self)
        for mod in self.screwdriver['modules']:
            shopping.buy(mod)
        self.dispatch_event("startup")

    def twist(self, host, port, factory):
        reactor.connectTCP(host, port, factory)

    def add_listener(self, name, listener):
        self.listeners[name.lower()].add(listener)

    def dispatch_event(self, name, *args):
        for dispatcher in self.listeners[name.lower()]:
            dispatcher(*args)

    def add_command(self, command, listener):
        #+ support subcommands
        if command in self.commands:
            raise SystemError
        self.commands[command] = listener

    def dispatch_command(self, command, *args):
        #+ subcommand dispatch
        #+ check for number of arguments
        if command in self.commands:
            self.commands[command](event, *args)
