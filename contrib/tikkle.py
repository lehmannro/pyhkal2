"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]
    - Abos requesten von DigestMod                [ ]
    - Ein und ausloggen via user.py               [x]


    user.py uebernimmt identitiy handling!!11!!1EINSELF
"""
from twisted.internet import defer
import re
__version__ = "0.1a"
__requires__ = ["irc"]


chaos("PenisViewUSER",
    """
        if (doc.tikkle) {
            emit(null, doc.tikkle)
        }
    """
)

@hook('privmsg')
@defer.inlineCallbacks
def startTheTikkleFun(event):
    event.reply("InFun")
    if (isinstance(event.target,irc.IRCChannel)):
        event.reply("InIf")
        # 1) Phrase basteln!
        msg = event.content

        # 2) Ist der User schon eingeloggt? bzw identity gelinkt?
        ident = event.source.identity if (hasattr(event.source,"identity")) else None

        ######## User ist eingeloggt
        if (ident != None):
            event.reply("InIf2")
            d = davenport.openDoc(event.source.identity.docid)
            doc = yield d

            loginRE = re.compile(doc["tikkle"]["login"])
            logoutRE = re.compile(doc["tikkle"]["logout"])
            afkRE = re.compile(doc["tikkle"]["afk"])
            event.reply("PreMatch")
            if (loginRE.match(event.content) != None):
                event.reply("doStuff() - ehehehe, Freddy B")
                doStuff()
            elif (logoutRE.match(event.content) != None):
                event.source.identity.avatars.remove(event.source)
                event.source.identity = None
                event.reply("Logged out?!")
            elif (afkRE.match(event.content) != None):
                # set last activity
                event.reply("Set Last activity!")

def doStuff():
    print "DOOOSTUUUUUUFFFFFFF!!!111222"

@hook('privmsg',expr='npx')
def MuupDuup(event):
    if (event.source.nick == 'npx'):
        event.source.identity = Identity("107097e10a2cacb7caa6d9d04d7ed8c7")
        event.source.identity.link(event.source)
        print "Locked n' Linked!"
