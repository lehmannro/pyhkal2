# coding: utf-8

hi(
    name = "stfu",
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

@hook("PRIVMSG", r"\b(\w+)\+\+") #+ unterschiedliche funktionen weil andere signatur
@register("++")
def karma_add(origin, *args):
    "increases karma by one"
    subject = args[0]
    karma = bot.get("karma", name=subject) + 1
    bot.update("karma", name=subject, karma)
    bot.send("%s hat nun ein Karma von %d" % (subject, karma))
    bot.send("ACHTUNG, KARMA!", dest=user.admins + [origin.public])

@register # äquivalent zu register("anderer_namespace")
def anderer_namespace(origin, *args):
    pass

@hook("shutdown")
def save():
    for chan in bot.get(NAME, ...):
        bot.setmode(chan, "-m")