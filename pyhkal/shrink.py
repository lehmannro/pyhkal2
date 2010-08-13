#!/usr/bin/env python

from _weakrefset import WeakSet

"""
Implementation of the Identity/Avatar scheme
"""

class Avatar(object):
    """
    Avatars represent the different 
    manifestations of Identities in
    different media/transports
    """

    def message_priv(msg):
        pass


class Identity(object):
    """
    Identities are unique reprenstations
    of media-independant identities that 
    can be linked to avatars

    Use id.avatars.add to add an avatar

    Avatars are removed automagically
    when all references are lost due 
    to weak references used by WeakSet
    """

    def __init__(self):
        self.avatars = WeakSet()

