"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]
    - Fetch tikkles                               [x]

"""
from twisted.internet import defer
import re
__version__ = "0.1a"
__requires__ = ["irc"]


tikkleView = chaos("tikkleTIKKLE",
    """
        if (doc.doctype == "tikkle") {
            emit(doc.to, [doc.from, doc.msg, doc._rev]);
        }
    """
)
tikkleIdentityView = chaos("tikkleIdentityView",
    """
        if (doc.doctype == "Identity") {
            emit("User", doc.name);
        }
    """
)

## Digest Control
@hook('irc.privmsg')
@defer.inlineCallbacks
def startTheTikkleFun(event):
    if ((isinstance(event.target,irc.IRCChannel)) and (hasIdentity(event))):
        d = davenport.openDoc(str(event.source.identity.docid))
        doc = yield d

        loginRE = re.compile(doc["tikkle"]["login"])
        logoutRE = re.compile(doc["tikkle"]["logout"])
        afkRE = re.compile(doc["tikkle"]["afk"])

        if (loginRE.match(event.content) != None):
            event.source.message("User recognized - Digests!")
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
    print "----------------"+str(entries)
    for entry in entries[u'rows']:
        if (entry[u'key'] == event.source.identity.docid):
            senderDoc = davenport.openDoc(str(entry[u'value'][0]))
            senderDoc = yield senderDoc
            event.source.message(str(senderDoc[u'name']+": "+entry[u'value'][1]))
            davenport.deleteDoc(str(entry[u'id']), str(entry[u'value'][2]))

## Send Messages
@hook('irc.privmsg',expr='^tikkle tikkle .*')
@defer.inlineCallbacks
def sendMsg(event):
    # msg = [tikkle, tikkle, <identity name>, <text>]
    msg = event.content.split(' ')
    if ((msg[1] == "tikkle") and (hasIdentity(event))):
        sent = False
        tikkle = {}
        users = yield tikkleIdentityView()
        for user in users[u'rows']:
            if (str(user[u'value']) == msg[2]):
                tikkle["from"] = event.source.identity.docid
                tikkle["to"] = user[u'id']
                tikkle["msg"] = " ".join(msg[3:])
                tikkle["doctype"] = "tikkle"
                davenport.saveDoc(tikkle)
                event.reply("Brief: "+str(tikkle))
                sent = True
                break
        if sent:
            event.reply("-done-")
        else:
            event.reply("Error: Identity DOES NOT COMPUTE!!1")
## AIDS
def hasIdentity(event):
    return not ((hasattr(event.source,"identity")) and (event.source.identity == None))

## Hardcoded Identity
@hook('irc.privmsg',expr='npx')
def MuupDuup(event):
    if ((event.source.nick == 'npx') and ((not hasattr(event.source,"identity")) or (event.source.identity == None))):
        event.source.identity = Identity('107097e10a2cacb7caa6d9d04d7ed8c7')
        event.source.identity.link(event.source)
        event.reply("User linked!")
    elif ((event.source.nick == 'ChosenOne') and ((not hasattr(event.source,"identity")) or (event.source.identity == None))):
        event.source.identity = Identity('7df575bf24c193a58bb74307a6d3eaca')
        event.source.identity.link(event.source)
        event.reply("User linked!")
