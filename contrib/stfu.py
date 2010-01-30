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

@register
def stfu(origin, args):
    dispatch_event('irc.send', "MODE %s +m" % origin.public)

@hook("shutdown")
def save():
    for chan in bot.get(NAME, "channels"):
        bot.setmode(chan, "-m")
