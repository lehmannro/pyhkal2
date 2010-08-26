# coding: utf-8

from pyhkal import shopping

#TODO: should we check in each command for parameter length?

__version__ = "0.1"

@defer.inlineCallbacks
def isadmin(source):
    if not source.identity:
        defer.returnValue(False) # cant be admin, haz no identity
    else: # check if identity is an admin 
        d = source.identity.fetch()
        identity = yield d
        defer.returnValue(identity.get(u'admin',False))


@register("load")
@defer.inlineCallbacks
def load_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content:
            try:
                shopping.buy(module)
            except BaseException as err: # gotta catch 'm all.
                event.reply("Error: %s" % err)

@register("reload")
@defer.inlineCallbacks
def reload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content:
            shopping.revoke(module)

@register("unload")
@defer.inlineCallbacks
def unload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content:
            shopping.renew(module)

@register("eval")
@defer.inlineCallbacks             
def eval_code(event):
    admin = yield isadmin(event.source)
    if admin:
        try:
            print event.content
            event.reply(eval(event.content))
        except Exception as err: # gotta catch 'm all.
            event.reply("Error: %s" % err)

@register("exec")
@defer.inlineCallbacks
def exec_code(event):
    admin = yield isadmin(event.source)
    if admin:
        exec event.content.split(" ", 1)[1] in globals()
