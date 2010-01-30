# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

from twisted.application import internet
from twisted.internet import protocol, reactor
from twisted.words.protocols import irc

DEFAULT_PORT = 6667
DEFAULT_NICK = "pyhkal"
DEFAULT_NAME = "PyHKAL 2.0"
DEFAULT_PREFIX = "!"

__doc__ = """
:Settings:
  irc
    server
      Host address.
    port
      Host port; defaults to %(DEFAULT_PORT)d.
    key
      Server connection password. Some IRC proxies will require your key to
      contain "username:password" because passwords are submitted before
      registration is completed.
    nick
      Initially desired pseudonym. It will be automatically adjusted if the
      nickname is already in use on sign-on. Most IRC servers impose certain
      rules on nicknames, eg. a maximum length of 15 characters, a restricted
      character set (word characters and ``[]\\\`^{|}``), no digits or hyphens
      in front of the nickname. Defaults to %(DEFAULT_NICK)s.
    name
      Real name; may contain spaces; defaults to "%(DEFAULT_NAME)s".
    user
      Username. This is your identity if not provided otherwise by an Ident
      Protocol daemon (:rfc:`1413`). Defaults to your nickname set in `nick`.
    prefix
      Trigger in messages to dispatch commands; defaults to
      ``%(DEFAULT_PREFIX)s``.
    channels
      List of channels which will be joined on sign-on. Channels need to start
      with any neccessary prefixes defined by the IRC server (eg. ``#`` or
      ``&``).
""" % locals()

@hook("send")
def send_message(message, dest):
    for d in dest:
        if d.type == "query":
            #+ spam queue für queries
            socket.send("PRIVMSG %s :%s" % (d, message))
        elif d.type == "channel":
            #+ spam queue für channels
            socket.send("PRIVMSG %s :%s" % (d, message))

class IRCClient(irc.IRCClient):
    def __init__(self):
        for name in dir(irc.IRCClient):
            def obj(self, *args):
                dispatch_event("irc."+name, *args)
            if not hasattr(IRCClient,name):
                setattr(self, name, obj)

    def connectionMade(self):
        def send(msg):
            print "Sending %s" % (msg,)
            self.sendLine(msg)
        hook("irc.send")(send)
        self._send = send
        irc.IRCClient.connectionMade(self)

    def kickedFrom(self, channel, kicker, message):
        dispatch_event("irc.kicked", channel, kicker, message)
        if channel in self.channels: # autorejoin
            self.join(channel)

    def privmsg(self, sender, recip, message):
        dispatch_event("irc.privmsg", sender, recip, message)
        if message.startswith(self.prefix):
            if " " in message:
                command, args = message.split(None, 1)
            else:
                command, args = message, []
            origin = Origin('channel', sender, recip)
            dispatch_command(origin, command[len(self.prefix):], args)
    def signedOn(self):
        dispatch_event("irc.signon")
        for channel in self.channels:
            self.join(channel)
    def modeChanged(self, user, channel, set, modes, args):
        dispatch_event("irc.modechange", user, channel, set, modes, args)
        if set:
            dispatch_event("irc.setmode", user, channel, modes, args)
        else:
            dispatch_event("irc.delmode", user, channel, modes, args)
    def lineReceived(self, data):  
        irc.IRCClient.lineReceived(self, data)
        spacetuple = data.split(' ')
        colontuple = data.split(':')
        numeric = spacetuple[1]
        #params = colontuple[2]
        print "<", numeric, ">", data       
        if numeric == '353':
            dispatch_event("irc.names", colontuple[2].split(' ')) # dirty list! like 


"""
2010-01-30 18:54:35+0100 [IRCClient,client] < JOIN > :PyHKAL3!PyHKAL2@server3.raumopol.de JOIN :#p

2010-01-30 18:54:35+0100 [IRCClient,client] < 353 > :port80a.se.quakenet.org 353 PyHKAL3 = #p :@Antesz @BMCT|JP`off CaTeYe PyHKAL3 @Q SaNci Scolo WA|4130 @esad gNu|boe @mark` @mrk` @si_- soma @wowbot @|Qlogged|
2010-01-30 18:54:35+0100 [IRCClient,client] < 366 > :port80a.se.quakenet.org 366 PyHKAL3 #p :End of /NAMES list.



354 <ich> <ziel> <auth>
315 <end of who>


353 channel names
366 "end of names list"

":port80a.se.quakenet.org 474 PyHKAL3 #' :Cannot join channel, you are banned (+b)"

"""

class IRCClientFactory(protocol.ReconnectingClientFactory):
    protocol = IRCClient
    initialDelay = 10.0
    factor = 1.6180339887498948 # Phi as math.e is too large
    maxDelay = 60 * 5
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        p.nickname = str(remember("irc nick", DEFAULT_NICK))
        p.realname = str(remember("irc name", DEFAULT_NAME))
        p.username = str(remember("irc user", None))
        p.password = str(remember("irc key", None))
        p.prefix = str(remember("irc prefix", DEFAULT_PREFIX))
        p.channels = map(str, remember("irc channels", []))
        return p
    def clientConnectionFailed(self, connector, reason):
        print reason.value
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

@hook("startup")
def establish_connection():
    factory = IRCClientFactory()
    server = remember("irc server")
    port = remember("irc port")
    #+ support SSL
    service = internet.TCPClient(server, port, factory)
    twist(service)
