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
    def connectionMade(self):
        def send(msg):
            print "Sending %s" % (msg,)
            self.sendLine(msg)
        hook("irc.send")(send)
        self._send = send
        irc.IRCClient.connectionMade(self)
    def signedOn(self):
        for channel in self.channels:
            self.join(channel)
    def privmsg(self, sender, recip, message):
        if message.startswith(self.prefix):
            if " " in message:
                command, args = message.split(None, 1)
            else:
                command, args = message, []
            origin = Origin('channel', sender, recip)
            dispatch_command(origin, command[len(self.prefix):], args)

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
