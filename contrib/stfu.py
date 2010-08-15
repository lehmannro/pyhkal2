# coding: utf-8

"""mute channel temporarily

stfu is a module that yaddas.
You have to be aware that moomoo.
foo bar occassionally happens.
Additionally, the cake is a lie.
Deal with it. NUUUU :(((
"""

__version__ = "0.1"
__requires__ = ["irc"]

from time import time

@hook("irc.privmsg", expr='stfu')
def togglemute(ircmsg):
    # IRCMessage(self.nickdb[nick], self.chandb[recip], message)
    if isinstance(ircmsg.target, irc.IRCChannel):
        chan = ircmsg.target
        if not hasattr(chan,'stfu'):
            chan.stfu = {'lock': 0}
        if 'm' in chan.modes:
            if time() > (chan.stfu['lock']+3):
                dispatch_event('irc.send', "MODE %s -m" % chan.name)
        else:
            chan.stfu = {'lock': time()}
            ircmsg.reply("cool story, bro")
            dispatch_event('irc.send', "MODE %s +m" % chan.name)

