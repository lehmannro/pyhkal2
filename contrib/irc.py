# encoding: utf-8

hi(
    version = "0.1",
    desc = "Internet Relay Chat transport layer",
)

from twisted.application import internet
from twisted.internet import protocol, reactor
from twisted.words.protocols import irc
from itertools import cycle

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
        self.whocounter = iter(cycle(xrange(1,1000)))
        self.whocallbacks = {}

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
        print "<>", modes, repr(args)
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
        #print "<", numeric, ">", data       
        if numeric == '353':
            dispatch_event("irc.names", spacetuple[4], colontuple[2].split(' ')) # dirty list! like ['@ChosenOne','+npx', 'crosbow']
        if numeric == "366":
            dispatch_event('irc.endofnames', spacetuple[3] )
    
        if numeric == "354":
            dispatch_event('irc.whorep', spacetuple[3:]) # generic hook, that will give you the answer, without knowing the question :D
            

    def getInfo(self, target, callback_result, callback_end):
        ID = whocounter.next()
        whocallbacks[ID] = (ID, callback_result, callback_end)
        if target[0] == '#':
            self.send("WHO %s %nafuhr,%s" % (target, ID))
        else: # nickname
            self.send("WHO %s, %nafuhr,%s" % (target, ID))
        
"""

id ident host nickname flags auth/0 realname

<< WHO #pyhkal, %nafuhrt,666
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 ~ai p4FE4D27B.dip.t-dialin.net ai H 0 :Always Innovating
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 ~olpc p4FE4D27B.dip.t-dialin.net olpc H 0 :Unknown
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 ~chosenone client-vpn-56.rz.ruhr-uni-bochum.de ChosenOne H+ 0 :chosenone
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 PyHKAL2 server3.raumopol.de PyHKAL3 H@ 0 :PyHKAL
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 npx noopman.users.quakenet.org NPX G+x noopman :NPENIX
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 ~saldana smitty.knid.net saldana H@ 0 :saldana
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 StruC server3.raumopol.de StruC H@ StruC :StruC
>> :clanserver4u1.de.quakenet.org 354 ChosenOne 666 stargaming server3.raumopol.de starGaming H@ stargaming :stargaming
>> :clanserver4u1.de.quakenet.org 315 ChosenOne #pyhkal, :End of /WHO list.

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
