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
        for module in event.content.split():
            try:
                shopping.buy(module)
            except BaseException as err: # gotta catch 'm all.
                event.reply("Error: %s" % err)
                return
        event.reply("Loading %s finished." % event.content)

@register("reload")
@defer.inlineCallbacks
def reload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content.split():
            shopping.renew(module)
        event.reply("Reloading %s finished." % event.content)

@register("unload")
@defer.inlineCallbacks
def unload_module(event):
    admin = yield isadmin(event.source)
    if admin:
        for module in event.content.split():
            shopping.revoke(module)
        event.reply("Unloading %s finished." % event.content)

@register("eval")
@defer.inlineCallbacks             
def eval_code(event):
    admin = yield isadmin(event.source)
    if admin:
        try:
            reply = eval(event.content)
        except Exception as err: # gotta catch 'm all.
            event.reply("Error: %s" % err)
        else:
            event.reply("> %r" % (reply,))

@register("exec")
@defer.inlineCallbacks
def exec_code(event):
    admin = yield isadmin(event.source)
    if admin:
        exec event.content in globals()
