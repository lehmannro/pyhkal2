#!/usr/bin/env python
"""
Implementation of Identity/Avatar scheme.

           +-----------+
           |   Event   | <- IRCMessage
           +-----------+ <- IRCNotice
           | + reply() | <- TwitterUpdate
           | - content |
           +-----------+
            |        |
            |        |
+-------------+     +-------------+
|    Avatar   |     |  Location   |
+-------------+     +-------------+
| + message() |     | + message() |
| - identity  |     +-------------+
+-------------+       ^  ^
 ^      #             |  IRCQuery    
IRCUser |             IRCChannel
        |
  +-----------+
  |  Identity |
  +-----------+
  | - avatars |
  +-----------+

"""

from _weakrefset import WeakSet
from weakref import WeakValueDictionary

class Avatar(object):
    """
    Avatars represent the different manifestations of identities in different
    communication channels.
    """

    def __init__(self):
        self.identity = None

    def message(self, msg):
        raise NotImplementedError

class Location(object):
    def message(self, msg):
        raise NotImplementedError

class MultitonMeta(type):
    def __init__(cls, name, bases, clsdict):
        cls.instances = WeakValueDictionary()
    def __call__(cls, unique, *args, **kwargs):
        if unique in cls.instances:
            return cls.instances[unique]
        else:
            o = type.__call__(cls, unique, *args, **kwargs)
            cls.instances[unique] = o
            return o

def IdentityFactory(service):
    class Identity(object):
        """
        Identities are abstract persons which persist throughout several sessions.
        They can be associated to several avatars.

        The `link` method adds an avatar to its available representation.

        Avatars are automatically removed when all references are lost due the
        reference's weakness.
        """

        __metaclass__ = MultitonMeta

        def __init__(self, docid):
            self.docid = docid
            self.avatars = WeakSet()

        def link(self, avatar):
            if avatar.identity not in (None, self):
                raise ValueError("double link from %r to %r and %r" %
                        (avatar, self, avatar.identity))
            service.dispatch_event("login", self, avatar)
            self.avatars.add(avatar)
            avatar.identity = self
            return self

        def fetch(self):
            return service.davenport.openDoc(self.docid)
    return Identity


class Event(object):
    def __init__(self, target, source, content):
        self.target = target
        self.source = source
        self.content = content

    def reply(self, msg):
        self.target.message(msg)

    def __repr__(self):
        return '<%s from %r to %r>' % (self.__class__.__name__, self.source, self.target)
