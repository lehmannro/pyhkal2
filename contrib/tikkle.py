"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]

"""
from twisted.internet import defer
import re
__version__ = "0.1a"
__requires__ = ["irc"]


tikkleView = chaos("tikkleTIKKLE",
    """
        if (doc.doctype == "tikkle") {
            emit(doc.to, [doc.from, doc.msg]);
        }
    """
)

@hook('privmsg')
@defer.inlineCallbacks
def startTheTikkleFun(event):
    if (isinstance(event.target,irc.IRCChannel)):
        # 1) Phrase basteln!
        msg = event.content

        # 2) Ist der User schon eingeloggt? bzw identity gelinkt?
        ident = event.source.identity if (hasattr(event.source,"identity")) else None

        ######## User ist eingeloggt
        if (ident != None):
            d = davenport.openDoc(str(event.source.identity.docid))
            doc = yield d

            loginRE = re.compile(doc["tikkle"]["login"])
            logoutRE = re.compile(doc["tikkle"]["logout"])
            afkRE = re.compile(doc["tikkle"]["afk"])

            if (loginRE.match(event.content) != None):
                event.reply("User recognized - Digests!")
                doStuff(event)
            elif (logoutRE.match(event.content) != None):
                event.source.identity.avatars.remove(event.source)
                event.source.identity = None
                event.reply("User unlinked!")
            elif (afkRE.match(event.content) != None):
                # set last activity
                event.reply("Set Last activity!")

def doStuff(event):
    fetchTikkles(event)

@defer.inlineCallbacks
def fetchTikkles(event):
    entries = yield tikkleView()
    for entry in entries[u'rows']:
        if (entry[u'key'] == event.source.identity.docid):
            event.reply(str(entry[u'value'][0]+": "+entry[u'value'][1]))

@hook('privmsg',expr='npx')
def MuupDuup(event):
    if ((event.source.nick == 'npx') and ((not hasattr(event.source,"identity")) or (event.source.identity == None))):
        event.source.identity = Identity(u'107097e10a2cacb7caa6d9d04d7ed8c7')
        event.source.identity.link(event.source)
        event.reply("User linked!")
