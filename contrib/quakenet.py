# coding: utf-8

"""Q Identity Avatar Pattern Binding
Association Interface Recource Dispatcher Factory
Deployment Abstract Validator Subscription

Actually, this module's task is /only/ to bind avatars to identities
"""

from twisted.web.error import Error

__version__ = "0.1"
__requires__ = ["irc"]
__author__ = "freddyb"

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
    for nickname, avatar in nickdb.iteritems():
        if avatar.identity is not None:
            continue
        if not getattr(avatar, 'auth', None):
            continue
        qauth = avatar.auth
        if qauth is not None:
            print "calling getAuths view, asking for nick %s auth %s" % (nickname, repr(qauth))
            try:
                result = yield getAuths(key=qauth)
            except Error:
                continue
            if len(result['rows']) > 0:
                docid = result['rows'][0]['id']
                identity = Identity(str(docid))
                identity.link(avatar)
                dispatch_event("irc.login", identity, avatar)
