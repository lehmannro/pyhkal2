# encoding: utf-8

"Internet Relay Chat transport layer"

__version__ = 0.1

from twisted.application import internet
from twisted.internet import protocol, reactor
from twisted.words.protocols import irc
from itertools import cycle
from types import MethodType

DEFAULT_PORT = 6667
DEFAULT_NICK = "pyhkal"
DEFAULT_NAME = "PyHKAL 2.0"
DEFAULT_PREFIX = "!"

__settings__ = dict(
    irc = dict(
        server = "Host address.",
        port = "Host port; defaults to %d." % DEFAULT_PORT,
        key = """Server connection password. Some IRC proxies will require
            your key to contain "username:password" because passwords are
            submitted before registration is complete.""",
        nick = """Initially desired pseudonym. It will be automatically
            adjusted if the nickname is already in use on sign-on. Most IRC
            servers impose certain rules on nicknames, eg. a maximum length of
            15 characters, a restricted character set (word characters and
            ``[]\\\`^{|}``), no digits or hyphens in front of the nickname.
            Defaults to %s.""" % DEFAULT_NICK,
        name = "Real name; may contain spaces; defaults to \"%s.\"" %
            DEFAULT_NAME,
        user = """Username. This is your identity if not provided otherwise by
            an Ident Protocol daemon (:rfc:`1413`). Defaults to your nickname
            set in `nick`.""",
        prefix = """Trigger in messages to dispatch commands; defaults to
            ``%s``.""" % DEFAULT_PREFIX,
        channels = """List of channels which will be joined on sign-on.
            Channels need to start with any neccessary prefixes defined by the
            IRC server (eg. ``#`` or ``&``).""",
    )
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

class IRCClient(irc.IRCClient):
    def __init__(self):
        for name in dir(irc.IRCClient): # Funktionen in twisted-ircclient
            def obj(self, *args):       #  definieren wir neu.
                dispatch_event("irc."+name, *args) # Erst werfen wir unseren Hook
                getattr(irc.IRCClient, "irc."+name)(*args) # und führen die "alte" twisted-funktion aus.
            obj = MethodType(obj,self) # (wir binden es an die Instanz..oder Klasse)
            if not hasattr(IRCClient,name): # aber nur falls wir sie nicht selbst weiter unten definiert haben..
                setattr(self, name, obj)    # nehmen wir die aus twisted. :)

        self.whocounter = iter(cycle(xrange(1,1000)))
        self.whocalls = {}
        self.whoresults = {}

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

    def isupport(self, options):
        pass
    """
    21:47 < ai> def isupport(options):
    21:47 < ai>     for option in options:
    21:47 < ai>         s = option.split('=')
    21:47 < ai>         if len(s) == 2:
    """

    def lineReceived(self, data):  
        irc.IRCClient.lineReceived(self, data)
        spacetuple = data.split(' ')
        colontuple = data.split(':')
        numeric = spacetuple[1]
        if numeric == '353':
            dispatch_event("irc.names", spacetuple[4], colontuple[2].split(' ')) # dirty list! like: ['@ChosenOne','+npx', 'crosbow']
        if numeric == "366":
            dispatch_event('irc.endofnames', spacetuple[3] )
    
        if numeric == "354":
            ":clanserver4u1.de.quakenet.org 354 ChosenOne 666 npx noopman.users.quakenet.org NPX G+x noopman :NPENIX"
            "                                    ^--me    ^--ID ^-ident ^--host              ^-nick^--flags^--auth ^--realname"
            resultdict = dict(zip( ('ident', 'host','nick','flags','auth','realname'), spacetuple[4:].split() ))
            resultdict['away'] = ('G' in resultdict['flags']) 
            resultdict['auth'] = None if (resultdict['auth'] == 0) else resultdict['auth']
            ID = spacetuple[3]            
            print "<<got authnickidentfooline>", repr(resultdict)
            dispatch_event('irc.whoreply', resultdict) # generic hook, that will give you the answer, without knowing the question :D
            if ID in whoresults: # how funny would "whoresluts" be,?! :P
                whoresults[ID].append(resultdict)
                
        if numeric == "315":
            ":clanserver4u1.de.quakenet.org 315 ChosenOne #pyhkal, :End of /WHO list."
            "                                               ^-spacetuple4            "

            target = spacetuple[4][:-1] # disregard comma with [:-1]
            (callback, ID) = whocalls[target]
            results = whoresults[ID]
            callback(results)  #we perform callback(list) here. the list is a list of resultdicts (resultdict-example see aboe)
            dispatch_event('irc.wholist', results)
            # we're done here, deleting..
            del(whocalls[target]) 
            del(whoresults[ID])

    def getInfo(self, target, callback_result):
        """ Example of sent command: WHO #pyhkal, %nafuhrt,666"""
        ID = whocounter.next()
        """
        whocalls: target -> callback,id
        whoresults: id -> (resultline,...)
        """
        whocalls[target] = (callback_result, ID)
        whoresults[ID] = []
        if target[0] == '#':
            self.send("WHO %s %nafuhr,%s" % (target, ID))
        else: # nickname
            self.send("WHO %s, %nafuhr,%s" % (target, ID))
     



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
