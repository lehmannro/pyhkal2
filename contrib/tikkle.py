"""

    Der fabuloese TikkleMod

    - Ein-/Auslog-Phrase                          [x]
    - AFK-Phrase                                  [x]
    - Abos requesten von DigestMod                [ ]
    - Ein und ausloggen via user.py               [x]

"""

__version__ = "0.1a"
__requires__ = ['user']


viewLOGIN = chaos("PenisViewLogin",
    """
        if (RegExp(doc.tikkle.login).test(%s)) {
            emit("penis",doc)
        }
    """ % phrase
)
viewAFK = chaos("PenisViewAFK",
    """
        if (RegExp(doc.tikkle.afk).test(%s)) {
            emit("penis",doc)
        }
    """ % phrase
)
viewLOGOUT = chaos("PenisViewLOGOUT",
    """
        if (RegExp(doc.tikkle.logout).test(%s)) {
            emit("penis",doc)
        }
    """ % phrase
)

@hook('PRIVMSG','/.*/')
def startTheTikkleFun(origin, args):
    if (origin.type == 'channel'):

        # 1) Phrase basteln!
        msg = ' '.join(args[1:])
        
        # 2) Ist der User schon eingeloggt?
        acc = user.getAccountByOrigin(origin)

        if (acc != None):                           ######## User ist eingeloggt
            """
                Digests?
                Afk setzen?
                Ausloggen?
            """
            ## Logout
            accounts = getAccountsThatMatchPhrase('logout', msg)
            for acc in accounts:
                if origin.user.lower() == acc["loggedinas"].lower():
                    user.logout(acc)
                    return None
            
            ## AFK setzen
            accounts = getAccountsThatMatchPhrase('afk', msg)
            for acc in accounts:
                if origin.user.lower() == acc["loggedinas"].lower():
                    user.setLastActivity(acc)
                    return None
            
            ## Digest
            accounts = getAccountsThatMatchPhrase('login', msg)
            for acc in accounts:
                if origin.user.lower() == acc["loggedinas"].lower():
                    doStuff(acc)
                    return None

        else:                                       ## User ist nicht eingeloggt
            accounts = getAccountsThatMatchPhrase('login', msg)
            for acc in accounts:
                def takeItToTheNextLevel(qauth):
                    if (qauth != ''):                            # User geauthed
                        if (qauth.lower() == acc["qauth"].lower()):
                            user.identify(origin)
                            return None
                    else:                                  # User nicht geauthed
                        irc.notice(origin.user, "PENIS PENIS PENIS PENIS PENIS PENIS! (... and a baseball bat...)")
                        return None
                channel.get_auth_nick(origin.user, takeItToTheNextLevel(qauth))

def getAccountsThatMatchPhrase(typ, phrase):
    if typ == 'afk':
        return viewAFK() ## afkphrase
    elif typ == 'logout':
        return viewLOGOUT() ## logoutphrase
    else
        return viewLOGIN() ## loginphrase

@hook("user.loggedin")
def doStuff(acc):
    irc.notice(origin.user, "hi %s! DIGESTS UND SO!" % acc)