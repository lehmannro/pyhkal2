# coding: utf-8

"""debug irc.privmsg hooks

this file is supposed to show you how to use regex- and generic hooks
"""

__version__ = "0.1"
__requires__ = ["irc"]


@hook("irc.privmsg")
def msg(sender, recip, message):
    """ test non-regex hook"""
    if message.startswith("debug"):
        print "<<!>> found debug-message!"


@hook("irc.privmsg", message=r"\b(\w+)\+\+")
def rmsg(sender, recip, message):
    """test regex hook  """
    #XXX Note that message has automagically become a SRE_MATCH Object, so handle with care!
    print "<<!>> Found debug-message via regex hook: %s -> %s (%s) " % (sender, recip, message.group(0)) # just print whole message
