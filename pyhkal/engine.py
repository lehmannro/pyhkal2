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
        self.listeners = collections.defaultdict(WeakSet)

    def startService(self):
        #XXX reloadable
        db = self.screwdriver['database']
        self.debug = self.screwdriver.get('debug', False)
        self.davenport = Davenport(db['host'], 'pyhkal', db['username'],
                db['password'], db.get('port', 5984))
        self.listeners.clear()
        self.commands = weakref.WeakValueDictionary()
        self.mall = shopping.checkout(self)
        for mod in self.screwdriver['modules']:
            shopping.buy(mod)
        self.dispatch_event("startup")

    def twist(self, *args):
        """twist([host,] port, factory)"""
        if len(args) == 2:
            reactor.listenTCP(*args)
        else:
            reactor.connectTCP(*args)

    def add_listener(self, name, listener):
        self.listeners[name.lower()].add(listener)

    def dispatch_event(self, name, *args):
        if self.debug:
            print "[%s] %r" % (name, args)
        for dispatcher in self.listeners[name.lower()]:
            dispatcher(*args)

    def add_command(self, command, listener):
        command = command.lower()
        #+ support subcommands
        if command in self.commands:
            raise SystemError
        self.commands[command] = listener

    def dispatch_command(self, command, event):
        command = command.lower()
        #+ subcommand dispatch
        #+ check for number of arguments
        if command in self.commands:
            self.commands[command](event)
