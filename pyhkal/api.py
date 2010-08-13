# encoding: utf-8

from functools import partial
from inspect import getargspec, currentframe
import types
import re
from pyhkal.engine import Pyhkal
from pyhkal.shrink import Avatar

api = {}
def apply(service):
    return dict((name, partial(func, service)
        if isinstance(func, (types.FunctionType, types.MethodType)) else func)
        for name, func in api.iteritems())

def expose(item_or_name, item=None):
    """
    >>> expose(obj) # requires obj to have __name__ attribute
    >>> @expose
    ... def func(): pass
    ...
    >>> expose("name", obj)
    """
    if item is not None:
        api[item_or_name] = item
    else:
        api[item_or_name.__name__] = item_or_name

@expose
def hook(service, event, *args, **kwargs):
    args = map(re.compile, args)
    for k in kwargs.iterkeys():
        kwargs[k] = re.compile(kwargs[k])

    # @hook('irc.sendmsg', recip=re1, msg=re2) ODER @hook('irc.sendmsg', re3) <- matcht auf sender
    # def handlemsg(sender,recip,msg) <- wird nur aufgerufen, wenn regex im Hook auch erfüllt ist!
    def deco(func):
        funcargs = getargspec(func)[0] # the new FunCarGS - order now!
        # dispatch_event('irc.privmsg', sender, recip, msg) --> ['sender','recip','msg']
        def matching( *margs, **mkwargs):
            params = dict(zip(funcargs, margs))
            params.update(mkwargs)
            value = dict(params)

            for i,arg in enumerate(args):
                match = arg.search(value[funcargs[i]])
                if not match:
                    return
                else:
                    params[funcargs[i]] = match

            for k,v in kwargs.iteritems():
                match = v.search(value[k])
                if not match:
                    return
                else:
                    params[k] = match

            func(**params)

        service.add_listener(event, matching)
        return matching
    return deco


@expose
def register(service, func_or_name):
    if isinstance(func_or_name, basestring):
        def wrapper(func):
            service.add_command(func_or_name, func)
            return func
        return wrapper
    service.add_command(func_or_name.__name__, func_or_name)
    return func_or_name

expose(Pyhkal.twist)

@expose
def chaos(service, name, script):
    mod = currentframe().f_back.f_globals['__mod__']
    service.davenport.order(mod, name, script)

@expose
def send(service, message, dest=None):
    service.dispatch_event('send', message)

_none = object()
@expose
def remember(service, breadcrumbs, default=_none):
    """Remember that random fact that popped into your head 2 AM in the
    morning. For some weird reason, you need a sofa to remember.

    """
    config = service.screwdriver
    try:
        return reduce(lambda doc, value: doc[value],
                breadcrumbs.split(), config)
    except KeyError:
        if default is not _none:
            return default
        raise

expose(Pyhkal.dispatch_command)
expose(Pyhkal.dispatch_event)

expose(Avatar)
