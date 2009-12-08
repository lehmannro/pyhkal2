#!/usr/bin/env python
# encoding: utf-8

from pyhkal.shopping import buy
from pyhkal.memo import remember, read as read_memo

commands = {}
modules = []
# dict of str -> (callback, dict of str -> (callback, dict ...))

def run(memo):
    read_memo(memo)
    for mod in remember("modules"):
        buy(mod)
    #+ config parsen
    #+ module laden
    #+ irc/web starten?


def dispatch_event(event, origin, args):
    pass
    #+ event dispatch

def dispatch_command(origin, command, *args):
    # Erwartet den Command in Listen-Form:
    # z.B.: ['rep', '-svn', 'install', 'stfumod']
    # Andere Transportschichten müssen dieses Format entsprechend einhalten.
    #+ subcommand dispatch
    #   !rep
    #     -svn ('install', 'stfumod')
    if command in commands:
        commands[command](origin, args)

def hi(**meta):
    """wirft möglicherweise eine Exception"""
    if 'depends' in meta:
        for dep in meta['depends']:
            setattr(mod, dep, load_module(dep))
            # macht bei depends="user": mod.user = usermod
    import sys
    mod = sys._stack_frame().f_previous #+ fixme
    mod.NAME = meta['name']
    mod.__metadata__ == meta #+ stack manipulation :-)

def register(function):
    name = function.__name__
    if name in commands:
        raise ModuleError("duplicate namespace")
    commands[name] == function
    return function

class Origin(object):
    def __init__(self, typ, user, public=None):
        self.type = typ # of (query, channel, notice, dcc, web)
        self.user = user
        self.public = public
# origin:
#   query (user)
#   notice (user, channel)
#   channel (user, channel)
#   dcc (user)
#   web (user)
