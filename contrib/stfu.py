# coding: utf-8

hi(
    version = "0.1",
    depends = [
      "irc>=0.1",
    ],
    author = "struc & starg", # ?? authors?
    desc = "mute channel temporarily",
)

"""
stfu is a module that yaddas.
You have to be aware that moomoo.
foo bar occassionally happens.
Additionally, the cake is a lie.
Deal with it. NUUUU :(((
"""


@register
def stfu(origin, args):
    irc.send("MODE %s +m" % origin.public)

@hook("shutdown")
def save():
    for chan in bot.get(NAME, "channels"):
        bot.setmode(chan, "-m")
