# encoding: utf-8

"Internet Relay Chat transport layer"

__version__ = 0.1

from twisted.application import internet
from twisted.internet import protocol, reactor, defer
from twisted.words.protocols import irc
from itertools import cycle
from types import MethodType
from time import time # for channel timestamp


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

class IRCUser(Avatar):
    def __init__(self, **kwargs):
        # Fall 2: Komplettes dict von nick, ident, host, realname, auth
        for k,v in kwargs.iteritems():
            setattr(self, k, v)
        assert self.nick != None

    @staticmethod
    def fromhostmask(hostmask): # Fall 1: IRCUser(hostmask="nick!ident@host") und er hat schonmal 3 Werte
        data = {}
        data["nick"], identandhost = hostmask.split('!', 1)
        data["ident"],data["host"] = identandhost.split('@',1)
        return IRCUser(**data)
        
    def message(self, text):
        dispatch_event("irc.sendmessage", self.nick, text)

class IRCChannel(Location):
    def __init__(self, name):
        self.name = name
        self.nicklist = []

    def updateTopic(self, topic, nick, timestamp=None):
        self.topic = topic
        self.topictimestamp = timestamp
        self.topicsetby = nick

    def updateTopicTS(self, nick, ts):
        self.topictimestamp  = ts
        self.topicsetby = nick

    def updateNames(self, nicklist): #xxx is not being called yet
        self.nicklist.append(nicklist)

    def updateModes(self, modes): #xxx is not being called yet
        self.modes = set(list(modes.replace('+','')))
        """
        i joined :wersfda!~werwt@p4FE4D637.dipself.t-dialin.net JOIN #pyhkal
        topic is :servercentral.il.us.quakenet.org 332 wersfda #pyhkal :foo
        topic was set at :servercentral.il.us.quakenet.org 333 wersfda #pyhkal ChosenOne 1281713634
        :servercentral.il.us.quakenet.org 353 wersfda @ #pyhkal :wersfda PyHKAL2 jannotb @ChosenOne catbot fishbot @npx @Q
        :servercentral.il.us.quakenet.org 366 wersfda #pyhkal :End of /NAMES list.
        """
    def message(self, msg):
        dispatch_event("irc.sendmessage", self.name, msg)

class IRCMessage(Event):
    def __init__(self, avatar, location, text):
        self.content = text
        self.source = avatar
        self.target = location

class IRCQuery(Location):
    def __init__(self, user):
        self.user = user

    def message(self, msg):
        dispatch_event("irc.sendmessage", self.user.nick, msg)

@hook("irc.sendmessage")
def send_message(message, dest):
    for d in dest:
        if d.type == "query":
            # FIXME there should be a function to get the username from an address
            # FIXME wrap around maximum length, is there something in twisted that will help us? ;)
            dispatch_event("irc.send", "PRIVMSG %s :%s" % (d.user.split("!")[0], message))
        elif d.type == "channel":
            dispatch_event("irc.send", "PRIVMSG %s :%s" % (d.public, message))

class IRCClient(irc.IRCClient, object):
    def __init__(self):
        """
        # vorher: dir(irc.IRCClient)
        for name in set(dir(irc.IRCClient)) - set(['yourHost']): # Funktionen in twisted-ircclient
            if callable(getattr(irc.IRCClient, name, name)) and not name.startswith("_"):
                print "in ircclient: ",name
                def obj(*args):       #  definieren wir neu.
                    print "Calling irc.", name, "with: ", args
                    dispatch_event("irc."+name, *args) # Erst werfen wir unseren Hook
                    getattr(irc.IRCClient, name)( *args) # und führen die "alte" twisted-funktion aus.
                obj = MethodType(obj,self, self.__class__) # (wir binden es an die Instanz..oder Klasse)
                if name not in self.__class__.__dict__: # aber nur falls wir sie nicht selbst weiter unten definiert haben..
                    setattr(self, name, obj)    # nehmen wir die aus twisted. :)
        """
        self.whocounter = iter(cycle(xrange(1,1000)))
        self.whocalls = {}
        self.whoresults = {}
        self.whoamount = 0
        self.nickdb = {}
        self.chandb = {}

    def UpdateNickDB(self, resultlist):
        for user in resultlist:
            self.nickdb[user['nick']] = IRCUser(**user)

        #print "UpdateToNickkDB:", resultlist
        #print "NickDB:", self.nickdb
    

    def connectionMade(self):
        irc.IRCClient.connectionMade(self)
        @hook("irc.send")
        def send(msg):
            print "Sending %s" % (msg,)
            self.sendLine(msg)
        self._send = send

    def kickedFrom(self, channel, kicker, message):
        irc.IRCClient.kickedFrom(self, channel, kicker, message)
        dispatch_event("irc.kicked", channel, kicker, message)
        if channel in self.channels: # autorejoin
            self.join(channel)

    def privmsg(self, sender, recip, message): # used when RECEIVING a message
        irc.IRCClient.privmsg(self, sender, recip, message)
        nick = sender.split("!",1)[0]
        if recip == self.nickname:
            dispatch_event("privmsg", IRCMessage(self.nickdb[nick], IRCQuery(self.nickdb[nick]), message))
        else:
            dispatch_event("privmsg", IRCMessage(self.nickdb[nick], self.chandb[recip], message))

        #dispatch_event("privmsg", origin, message)
        #if message.startswith(self.prefix):
        #    if " " in message:
        #        command, args = message.split(None, 1)
        #    else:
        #        command, args = message, []
        #    dispatch_command(origin, command[len(self.prefix):], args)

    def noticed(self, sender, recip, message):
        # the original noticed-function just passes its arguments towards privmsg() - we dont want to do that!
        pass
        #FIXME the lines below are just copied from privmsg - how appropriate this is I dont know
        #if recip == self.nickname:
        #    origin = Origin('query', sender, recip)
        #else:
        #    origin = Origin('channel', sender, recip)
        #dispatch_event("irc.notice", sender, recip, message) # remember, that we MUST NEVER respont
        #dispatch_event("notice", origin, message)            # automatically on notices

    def signedOn(self):
        irc.IRCClient.signedOn(self)
        dispatch_event("irc.signon")
        for channel in self.channels:
            self.join(channel)

    def modeChanged(self, user, channel, set, modes, args):
        irc.IRCClient.modeChanged(self, user, channel, set, modes, args)
        dispatch_event("irc.modechange", user, channel, set, modes, args)
        if set:
            dispatch_event("irc.setmode", user, channel, modes, args)
        else:
            dispatch_event("irc.delmode", user, channel, modes, args)

    def userRenamed(self, oldname, newname):
        self.nickdb[newname] = self.nickdb.pop(oldname)

    def joined(self, channel):
        self.chandb[channel] = IRCChannel(channel)
        d = self.getInfo(channel)
        d.addCallback(self.UpdateNickDB)


    def topicUpdated(self, user, channel, newTopic):
        self.chandb[channel].updateTopic(newTopic, user, timestamp=int(time()) )

    def irc_JOIN(self, prefix, params):
        irc.IRCClient.irc_JOIN(self, prefix, params)
        nick = prefix.split('!', 1)[0]
        if not nick in self.nickdb:
            self.nickdb[nick] = IRCUser.fromhostmask(prefix)

    def irc_QUIT(self, prefix, params):    	    
        irc.IRCClient.irc_QUIT(self, prefix, params)
        nick = prefix.split('!', 1)[0]
        del(self.nickdb[nick])

    def lineReceived(self, data): 
        irc.IRCClient.lineReceived(self, data)
        print ">> ", data
        spacetuple = data.split(' ')
        colontuple = data.split(':')
        numeric = spacetuple[1]

        if numeric == '333':
            self.chandb[spacetuple[3]].updateTopicTS(spacetuple[4], spacetuple[5])

        if numeric == '353': # name-answer
            ":clanserver4u1.de.quakenet.org 353 ChosenOne = #chan :@alice +bob charlie"
            for nickname in colontuple[2].split(' '):
                nick = nickname.replace('+','').replace('@','')
                if ('@' in nickname) or ('+' in nickname):
                    mode = nickname[0]
                else:
                    mode = ""
                self.chandb[spacetuple[4]].nicklist.append( {nick: mode } )
        if numeric == "366": # end of /names list
            dispatch_event('irc.endofnames', spacetuple[3] )
    
        if numeric == "354": # triggers on custom /who like the one in getInfo()
            """ :clanserver4u2.de.quakenet.org 354 pyhkal_ #pyhkal ~ChosenOne ChosenOne.users.quakenet.org ChosenOne H@+x ChosenOne :lost in thoughts
            :clanserver4u2.de.quakenet.org 354 pyhkal_ #pyhkal TheQBot CServe.quakenet.org Q H*@d Q :The Q Bot
            :clanserver4u1.de.quakenet.org 354 ChosenOne 666 npx noopman.users.quakenet.org NPX G+x noopman :NPENIX
                                                 ^--me    ^--ID ^-ident ^--host              ^-nick^--flags^--auth ^--realname
                 in case of missing ID:                ident---v
                :wineasy2.se.quakenet.org 354 wewetrasdgfdg PyHKAL2 server3.raumopol.de PyHKAL2 H 0 :PyHKAL

            """
            if spacetuple[3].isdigit() or spacetuple[3][0] == '#':
                resultdict = dict(zip( ('ident', 'host', 'nick', 'flags', 'auth', 'realname'), spacetuple[4:9] + [colontuple[2],] ))
                resultdict['away'] = ('G' in resultdict['flags']) 
                resultdict['auth'] = None if (resultdict['auth'] == 0) else resultdict['auth']
                ID = spacetuple[3] #this might be our numeric ID or the channel matching our rquest
                #print "<<got authnickidentfooline>", repr(resultdict), ID
                if ID in self.whoresults: # WHO results. how funny would "whore-sluts" be,?! :P
                    self.whoresults[ID].append(resultdict)
                else:
                    self.whoresults[ID] = [resultdict]
                
        if numeric == "315": # end of /who list
            ":clanserver4u1.de.quakenet.org 315 ChosenOne #pyhkal, :End of /WHO list."
            "                                               ^-spacetuple4            "
            self.whoamount -= 1
            if self.whoamount == 0: #
                # We cannot assure, which WHO-reply ends here, so we have to wait for ALL current requests to finish.
                for ID in self.whoresults:
                    #print "res:", repr(self.whoresults), "id", repr(ID)
                    d, target = self.whocalls[ID]
                    if len(self.whoresults[ID]) > 0:
                        d.callback(self.whoresults[ID])
                    else:
                        d.errback(ValueError())
            self.whocalls = {}
            self.whoresults = {}

    def getInfo(self, target):
        """ Example of sent command: WHO #pyhkal, %nafuhrt,666"""
        ID = self.whocounter.next()
        """
        whocalls: target -> callback,id
        whoresults: id -> (resultline,...)
        """
        d = defer.Deferred()
        if target[0] == '#':
            self.whocalls[target] = (d, target)
            self.whoresults[target] = []
            dispatch_event("irc.send", "WHO %s n%%cnafuhr" % target)
        else: # nickname
            self.whocalls[ID] = (d, target)
            self.whoresults[ID] = []
            dispatch_event("irc.send", "WHO %s, n%%nafuhr,%s" % (target, ID))
        self.whoamount += 1
        return d
     

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
        p.lineRate = 1/self.factor;
        return p
    def clientConnectionFailed(self, connector, reason):
        print reason.value
        protocol.ReconnectingClientFactory.clientConnectionFailed(self, connector, reason)

@hook("startup")
def establish_connection():
    factory = IRCClientFactory()
    server = remember("irc server")
    port = remember("irc port", DEFAULT_PORT)
    #+ support SSL
    twist(server, port, factory)

#TODO
"""
ideas for irc.py
    - regexcallbacks registrieren über
        setCallback(funktionsname, regex)
            -> self.callbacks.append = (func, re)
        und dann in der privmsg-funktion: foreach self.callbacks:
            if re-match -> func(msginhalt)

    - test für getInfo!!1

    - on join (hab ich laub ich)
    - on part/kick überprüfen, ob wir denjenigen noch "sehen".
    -> insbesondere nicklist-updates in part,quit,join,kick,nick

    wichtig: das füllen von chandb prüfen :)

    - prefix/serveroptions
        diskussion ob severoptions['PREFIX'] durch ein nonstring ersetzt werden sollte..

     - users.quakenet.org automatisch in <user>.auth einbringen :)

channel.py klugscheiß-todo
    - prefix/mode-chars sind konstant enthalten, statt auf irc.serveroptions zu gehen
    - who-requests wreden noch selbsttätig angefertigt -> getInfo nutzen
    - peni muss raus ;D, genauso wie callback(Janno)






"""


