# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

DEFAULT_PORT = 6667

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

@hook("startup")
@thread
def establish_connection():
    s = socket.socket()
    send = lambda line: s.send(line + "\n")
    server = remember("irc server")
    port = remember("irc port", DEFAULT_PORT)
    s.connect((server, port))
    send("USER pyhkal pyhkal pyhkal :PyHKAL")
    send("NICK PyHKAL2")
    buf = ""
    while 1:
        buf += s.recv(1024)
        while 1:
            eolpos = buf.find("\r\n")
            if eolpos == -1:
                break
            line = buf[:eolpos]
            if line.startswith("PING :"):
                send(line.replace("PING :", "PONG "))
            elif line.startswith(":"):
                line = line.split()
                if line[1] == "376":
                    for channel in remember("irc channels", []):
                        send("JOIN %s" % channel)
            buf = buf[eolpos+2:]
#    if x.match("PRIVMSG * :!*"): #+ prefix aus der config laden
#        origin, command = x.matches()
        #+ in WebMod: x.split("/")
#        dispatch_command(IRCChannel(origin), command)
#    else:
#        _, event, *args = x.split()
#        dispatch_event(event, args)
