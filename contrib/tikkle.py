"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]
    - Abos requesten von DigestMod                [ ]
    - Ein und ausloggen via user.py               [x]


    user.py uebernimmt identitiy handling!!11!!1EINSELF
"""
from twisted.internet import defer

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
    if (isinstance(event,irc.IRCChannel)):

        # 1) Phrase basteln!
        msg = event.content

        # 2) Ist der User schon eingeloggt? bzw identity gelinkt?
        ident = event.source.identity

        ######## User ist eingeloggt
        if (ident != None):
            d = davenport.openDoc(event.ident.docid)
            doc = yield d

            loginRE = re.compile(doc.tikkle.login)
            logoutRE = re.compile(doc.tikkle.logout)
            afkRE = re.compile(doc.tikkle.afk)

            if (loginRE.match(event.content) != None):
                doStuff()
            elif (logoutRE.match(event.content) != None):
                event.source.ident.avatars.remove(event.source)
                event.source.ident = None
                print "Logged out?!"
            elif (afkRE.match(event.content) != None):
                # set last activity
                print "Set Last activity!"

@hook('privmsg')
def mumupupu(event):
    print "FUBARUBARUBARUBARUBRAURBA PENIS!-------------"
    event.reply('fubardubar')

@hook("user.loggedin")
def doStuff(acc):
    irc.notice(origin.user, "hi %s! DIGESTS UND SO!" % acc)
