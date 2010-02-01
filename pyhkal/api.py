# encoding: utf-8

import inspect
from distutils.version import LooseVersion
from twisted.application.service import Service
from inspect import getargspec
import re
import pyhkal.davenport
import pyhkal.engine
import pyhkal.fred
import pyhkal.origin
import pyhkal.shopping


api = {}
def expose(item_or_name, item=None):
    """
    >>> expose(obj) # requires obj to have __name__ attribute
    >>> @expose
    ... def func(): pass
    ...
    >>> expose("name", obj)
    """
    if item:
        api[item_or_name] = item
    else:
        api[item_or_name.__name__] = item_or_name

@expose
def hook(event, *args, **kwargs):
    args = map(re.compile, args)
    for k in kwargs.iterkeys():
        kwargs[k] = re.compile(kwargs[k])

    # @hook('irc.sendmsg', recip=re1, msg=re2) ODER @hook('irc.sendmsg', re3) <- matcht auf sender
    # def handlemsg(sender,recip,msg) <- wird nur aufgerufen, wenn regex im Hook auch erfüllt ist!
    def deco(func):
        funcargs = getargspec(func).args # the new FunCarGS - order now!
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

        pyhkal.engine.add_listener(event, func)
        return matching
    return deco


@expose
def register(func_or_name):
    if isinstance(func_or_name, basestring):
        def wrapper(func):
            pyhkal.engine.add_command(func_or_name, func)
            return func
        return wrapper
    pyhkal.engine.add_command(func_or_name.__name__, func_or_name)
    return func_or_name

expose("twist", pyhkal.engine.add_service)

@expose
def send(message, dest=None):
    pyhkal.engine.dispatch_event('send', message)

expose(pyhkal.davenport.chaos)
expose(pyhkal.davenport.order)
expose(pyhkal.davenport.remember)
expose(pyhkal.davenport.stash)
expose(pyhkal.engine.dispatch_command)
expose(pyhkal.engine.dispatch_event)
expose("thread", pyhkal.fred.threaded)
expose(pyhkal.origin.Origin)
