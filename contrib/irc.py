# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

import socket

@hook("send")
def send_message(message, dest):
    for d in dest:
        if d.type == "query":
            #+ spam queue für queries
            socket.send("PRIVMSG %s :%s" % (d, message))
        elif d.type == "channel":
            #+ spam queue für channels
            socket.send("PRIVMSG %s :%s" % (d, message))

@thread
@hook("startup")
def establish_connection():
    s = socket.socket()
    if x.match("PRIVMSG * :!*"): #+ prefix aus der config laden
        origin, command = x.matches()
        #+ in WebMod: x.split("/")
        dispatch_command(IRCChannel(origin), command)
    else:
#        _, event, *args = x.split()
        dispatch_event(event, args)
