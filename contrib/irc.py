# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

"""
"""

from twisted.words.protocols import irc
from twisted.internet import protocol, reactor


DEFAULT_PORT = 6667
DEFAULT_NICK = "pyhkal"
DEFAULT_NAME = "PyHKAL 2.0"
DEFAULT_PREFIX = "!"

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
        irc.IRCClient.connectionMade(self)
        hook("send")(self.sendLine)
    def signedOn(self):
        for channel in self.channels:
            self.join(channel)
    def privmsg(self, sender, recip, message):
        if message.startswith(self.prefix):
            if " " in message:
                command, args = message.split(None, 1)
            else:
                command, args = message, []
            dispatch_command(None, command[len(self.prefix):], args)

class IRCClientFactory(protocol.ReconnectingClientFactory):
    protocol = IRCClient
    initialDelay = 10.0
    factor = 1.7071067811865475 # Phi
    maxDelay = 60 * 5
    def buildProtocol(self, addr):
        p = self.protocol()
        p.factory = self
        p.nickname = remember("irc nick", DEFAULT_NICK)
        p.realname = remember("irc name", DEFAULT_NAME)
        p.username = remember("irc user", None)
        p.password = remember("irc key", None)
        p.prefix = remember("irc prefix", DEFAULT_PREFIX)
        p.channels = remember("irc channels", [])
        return p
    def clientConnectionFailed(self, connector, reason):
        print reason.value
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

@hook("startup")
def establish_connection():
    factory = IRCClientFactory()
    server = remember("irc server")
    port = remember("irc port")
    reactor.connectTCP(server, port, factory)
