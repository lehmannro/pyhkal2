# coding: utf-8

"""Q Identity Avatar Pattern Binding
Association Interface Recource Dispatcher Factory
Deployment Abstract Validator Subscription

Actually, this module's task is /only/ to bind avatars to identities
"""
from twisted.internet import defer
__version__ = "0.1"
__requires__ = ["irc"]

getAuths = chaos("getAuths","""
    if (doc.qauth) {
        emit(doc.qauth, null);
    } 
    """
    )


@hook("irc.updatenickdb")
@defer.inlineCallbacks
def findIdentities(nickdb):
    #key in nickdb =  nickname
    # value für nicckdb[nickname] = IRCUser{ nick: .., auth: ..., realname: ... }
    for nickname in nickdb:
        if hasattr(nickdb[nickname], 'auth'):
            qauth = nickdb[nickname].auth
            if (qauth != None):
                print "calling getAuths view, asking for nick %s auth %s" % (nickname, repr(qauth))
                result = yield getAuths(key=qauth)
                if len(result[u'rows']) > 0:
                    docid = result[u'rows'][0][u'id']
                    #print "Foo-Yielding:", nickname, "id of user", docid
                    identity = Identity(str(docid))
                    identity.link(nickdb[nickname])
                    nickdb[nickname].identity = identity
                    dispatch_event("irc.login", identity, nickdb[nickname])
    # identity.avatars.add(ircuseer)
    # nickdb[nickdb].identity = identity


