# coding: utf-8

from pyhkal import shopping
from twisted.internet import defer

#TODO: should we check in each command for parameter length?

__version__ = "0.1"
__requires__ = ["irc"]

@defer.inlineCallbacks
def isadmin(source):
    if not source.identity:
        defer.returnValue(False) # cant be admin, haz no identity
    else: # check if identity is an admin 
        d = source.identity.fetch()
        identity = yield d
        defer.returnValue(identity.get(u'admin',False))


@hook("load")
@defer.inlineCallbacks
def load_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content.split(" ")[1:]:
            try:
                shopping.buy(module)
            except BaseException as err: # gotta catch 'm all.
                event.reply("Error: %s" % err)

@register("reload")
@defer.inlineCallbacks
def reload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content.split(" ")[1:]:
            shopping.revoke(module)

@register("unload")
@defer.inlineCallbacks
def unload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content.split(" ")[1:]:
            shopping.renew(module)

@register("eval")
@defer.inlineCallbacks             
def eval_code(event):
    admin = yield isadmin(event.source)
    if admin:
        try:
            event.reply(eval(event.content.split(" ", 1)[1]))
        except Exception as err: # gotta catch 'm all.
            event.reply("Error: %s" % err)

@register("exec")
@defer.inlineCallbacks
def exec_code(event):
    admin = yield isadmin(event.source)
    if admin:
        exec event.content.split(" ", 1)[1] in globals()

@hook("message", expr="!addidentiy") # "Was hat sich der Autor dabei gedacht?"
def foo(event):
    pass
