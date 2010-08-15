"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]
    - Fetch tikkles                               [x]

"""
from twisted.internet import defer
import re
import datetime

__version__ = "0.1a"
__requires__ = []


tikkleView = chaos("tikkleTIKKLE",
    """
        if (doc.doctype == "tikkle") {
            emit(doc.to, [doc.from, doc.msg, doc._rev, doc.time]);
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

@hook('message')
@defer.inlineCallbacks
def startTheTikkleFun(event):
    if (hasIdentity(event)):
        d = davenport.openDoc(str(event.source.identity.docid))
        doc = yield d
        loginRE =  re.compile(doc["tikkle"]["login"])
        if (loginRE.match(event.content) != None):
            event.source.message("User recognized - Digests!")
            doStuff(event)

def doStuff(event):
    fetchTikkles(event)

@defer.inlineCallbacks
def fetchTikkles(event):
    entries = yield tikkleView(key=event.source.identity.docid)
    for entry in entries[u'rows']:
        senderDoc = davenport.openDoc(str(entry[u'value'][0]))
        senderDoc = yield senderDoc
        mtime = datetime.datetime.fromtimestamp(entry[u'value'][2]).strftime("[%d.%m|%H:%M]")
        event.source.message(mtime+" <"+str(senderDoc[u'name']+"> "+entry[u'value'][1]))
        davenport.deleteDoc(str(entry[u'id']), str(entry[u'value'][2]))

## Send Messages
@hook('message',expr='^tikkle tikkle .*')
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
                tikkle["time"] = int(datetime.datetime.now().strftime("%s"))
                tikkle["from"] = event.source.identity.docid
                tikkle["to"] = user[u'id']
                tikkle["msg"] = " ".join(msg[3:])
                tikkle["doctype"] = "tikkle"
                davenport.saveDoc(tikkle)
                print "[TIKKLE] SENT MESSAGE: "+str(tikkle)
                event.reply("Brief: "+str(tikkle))
                sent = True
                break
        if sent:
            event.source.message("Message successfully sent!")

## AIDS
def hasIdentity(event):
    return not ((hasattr(event.source,"identity")) and (event.source.identity == None))
