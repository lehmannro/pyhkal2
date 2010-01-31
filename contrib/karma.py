__version__ = "0.1"

@hook("PRIVMSG", r"\b(\w+)\+\+") #+ unterschiedliche funktionen weil andere signatur
@register("++")
def karma_add(origin, *args):
    "increases karma by one"
    subject = args[0]
    karma = bot.get("karma", name=subject) + 1
    bot.update("karma", name=subject, value=karma)
    bot.send("%s hat nun ein Karma von %d" % (subject, karma))
    bot.send("ACHTUNG, KARMA!", dest=user.admins + [origin.public])
