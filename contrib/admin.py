# coding: utf-8

from pyhkal import shopping

__version__ = "0.1"
__requires__ = ["irc"]

def isadmin(source):
    # return True
    return source.nick == "saldana"
    # return hasattr(source, identity) and hasattr(source.identity, admin) and source.identity.admin


@hook("privmsg", expr="!load\s.+")
def load_module(event):
    if isadmin(event.source):
        for module in event.content.split(" ")[1:]:
            try:
                shopping.buy(module)
            except BaseException as err: # gotta catch 'm all.
                event.reply("Error: %s" % err)

@hook("privmsg", expr="!reload\s.+")
def reload_module(event):
    if isadmin(event.source):
        for module in event.content.split(" ")[1:]:
            shopping.revoke(module)

@hook("privmsg", expr="!unload\s.+")
def unload_module(event):
    if isadmin(event.source):
        for module in event.content.split(" ")[1:]:
            shopping.renew(module)

@hook("privmsg", expr="!eval\s.+")
def eval_code(event):
    if isadmin(event.source):
        try:
            event.reply(eval(event.content.split(" ", 1)[1]))
        except Exception as err: # gotta catch 'm all.
            event.reply("Error: %s" % err)

@hook("privmsg", expr="!exec\s.+")
def exec_code(event):
    if isadmin(event.source):
        exec event.content.split(" ", 1)[1] in globals()

@hook("privmsg", expr="!addidentiy")
def foo(event):
    pass
