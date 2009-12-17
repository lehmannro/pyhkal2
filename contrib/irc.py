# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

DEFAULT_PORT = 6667
DEFAULT_NICK = "pyhkal"
DEFAULT_USER = "pyhkal"
DEFAULT_NAME = "PyHKAL 2.0"
DEFAULT_PREFIX = "!"

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
    nick = remember("irc nickname", DEFAULT_NICK)
    user = remember("irc username", DEFAULT_USER)
    name = remember("irc realname", DEFAULT_NAME)
    pwd = remember("irc password", None)
    send("USER %s * * :%s" % (user, name))
    if pwd:
        send("PASS %s" % pwd)
    send("NICK %s" % nick)
    prefix = ":" + remember("irc prefix", DEFAULT_PREFIX)
    buf = ""
    while 1:
        buf += s.recv(1024)
        while 1:
            eolpos = buf.find("\r\n")
            if eolpos == -1:
                break
            line = buf[:eolpos]
            if line.startswith("PING :"):
                send(line.replace("PING", "PONG "))
            elif line.startswith(":"):
                line = line.split()
                if line[1] == "376": # RPL_ENDOFMOTD
                    for channel in remember("irc channels", []):
                        send("JOIN %s" % channel)
                elif line[1] == "433": # ERR_NICKNAMEINUSE
                    send("NICK %s-" % line[3])
                elif line[1] == "PRIVMSG": # Private messages
                    if line[3].startswith(prefix):
                        dispatch_command(None, line[3][len(prefix):], line[4:])
            buf = buf[eolpos+2:]
