# encoding: utf-8

hi(
    name = "irc",
    version = "0.1",
    desc = "irc transport layer",
)

@hook("send")
def send_message(message, dest):
    for d in dest:
        if d.type == "query":
            #+ spam queue für queries
            socket.send("PRIVMSG %s :%s" % (d, message))
        elif d.type == "channel":
            #+ spam queue für channels
            socket.send("PRIVMSG %s :%s" % (d, message))


while 0: #+ async
    if x.match("PRIVMSG * :!*"): #+ prefix aus der config laden
        origin, command = x.matches()
        #+ in WebMod: x.split("/")
        dispatch_command(IRCChannel(origin), command)
    else:
#        _, event, *args = x.split()
        dispatch_event(event, args)
