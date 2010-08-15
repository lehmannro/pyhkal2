# encoding: utf-8

__version__ = "0.0"

from twisted.internet import reactor

@register("timer")
def timer(event):
    args = event.content.split(" ", 1)
    if len(args) >= 2 and args[0].isdigit():
        # TODO add nickname when there's a generice property
        reactor.callLater(int(args[0]), event.reply, u"Timer: %s" % args[1])
    else:
        event.reply("timer <delay in seconds> <message>")
