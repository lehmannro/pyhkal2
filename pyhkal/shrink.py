#!/usr/bin/env python
"""
Implementation of Identity/Avatar scheme.

           +-----------+
           |   Event   |
           +-----------+
           | + reply() |
           | - content |
           +-----------+
            |        |
            |        |
+-------------+     +-------------+
|    Avatar   |     |  Location   |
+-------------+     +-------------+
| + message() |     | + message() |
| - identity  |     +-------------+
+-------------+
       #
       |
       |
 +-----------+
 |  Identity |
 +-----------+
 | - avatars |
 +-----------+

"""

from _weakrefset import WeakSet

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


def IdentityFactory(service):
    class Identity(object):
        """
        Identities are abstract persons which persist throughout several sessions.
        They can be associated to several avatars.

        The `link` method adds an avatar to its available representation.

        Avatars are automatically removed when all references are lost due the
        reference's weakness.
        """

        INSTANCES = {}
        def __new__(cls, docid):
            if docid not in cls.INSTANCES:
                cls.INSTANCES[docid] = object.__new__(cls, docid)
            return cls.INSTANCES[docid]

        def __init__(self, docid):
            self.docid = docid
            self.avatars = WeakSet()

        def link(self, avatar):
            if avatar.identity not in (None, self):
                raise ValueError("double link from %r to %r and %r" %
                        (avatar, self, avatar.identity))
            self.avatars.add(avatar)
            avatar.identity = self
            return self

        def fetch(self):
            return service.davenport.openDoc(self.docid)


class Event(object):
    def __init__(self, target, source, content):
        self.target = target
        self.source = source
        self.content = content

    def reply(self, msg):
        self.target.message(msg)
