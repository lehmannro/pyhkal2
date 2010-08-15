#!/usr/bin/env python
# coding: utf-8

from twittytwister.twitter import Twitter
from oauth import oauth
from functools import partial
from twisted.internet.task import LoopingCall
from collections import defaultdict


REFRESHDELAY = 60

"""
dict of since_id values for every task
to be executed repeatedly
this could be reworked to a single value
see refresh_task
"""
since_id = -1


import re, htmlentitydefs

##
# Taken from http://effbot.org/zone/re-sub.htm#unescape-html
# Removes HTML or XML character references and entities from a text string.
#
# @param text The HTML (or XML) source text.
# @return The plain text, as a Unicode string, if necessary.

def unescape(text):
    def fixup(m):
        text = m.group(0)
        if text[:2] == "&#":
            # character reference
            try:
                if text[:3] == "&#x":
                    return unichr(int(text[3:-1], 16))
                else:
                    return unichr(int(text[2:-1]))
            except ValueError:
                pass
        else:
            # named entity
            try:
                text = unichr(htmlentitydefs.name2codepoint[text[1:-1]])
            except KeyError:
                pass
        return text # leave as is
    return re.sub("&#?\w+;", fixup, text)



twitterIdentityView = chaos("twitterIdentityView",
    """
        if (doc.doctype == "Identity") {
            emit(doc.twitter, null);
        }
    """
    )



con = oauth.OAuthConsumer(
                remember('twitter consumer key'),
                remember('twitter consumer secret')
            )
tok = oauth.OAuthToken(
                remember('twitter token key'),
                remember('twitter token secret')
            )



def extract_id(str):
    id = str.rsplit('/',1)[1]
    assert id.isdigit()
    return id


class Tweet(Event):
    def __init__(self, target, source, content, id):
        Event.__init__(self, target, source, content)
        self.id = id
    def reply(self, msg):
        return self.target.reply("@%s %s" % (self.source.name, msg))


class TwitterLoc(Location):
    def __init__(self, id):
        self.id = id

    def message(self, msg, params=None):
        return tweet(msg, params)

    def reply(self, msg):
        return self.message(
                    msg,
                    params={'in_reply_to_status_id':self.id}
                )
class Reply(TwitterLoc):
    pass

class Friend(TwitterLoc):
    pass

class Mention(TwitterLoc):
    pass

class User(Avatar):
    __metaclass__ = MultitonMeta
    def __init__(self, name):
        Avatar.__init__(self)
        self.name = name
        self.identity_deferred = self.identify()

    @defer.inlineCallbacks
    def identify(self):
        res = yield twitterIdentityView(key=self.name)
        if res['rows']:
            identity = Identity(res['rows'][0]['id'])
            identity.link(self)

    def message(self, msg, params=None):
        return twit().send_direct_message(msg, self.name, params)
    def __eq__(self, obj):
        return isinstance(obj, User) and self.name.lower() == obj.name.lower()
    def __hash__(self):
        return hash(self.name.lower())


def twit():
    return Twitter(consumer=con, token=tok)

def tweet(msg, params=None):
    params = params or {}
    return twit().update(msg,  params=params)

def tweet_direct(msg, user, params=None):
    params = params or {}
    return twit().send_direct_message(msg, screen_name=user, params=params)







def atom_collect(collection, delegate, msg):
    msg_id = extract_id(msg.id)
    collection[msg_id] = msg, delegate

def xml_collect(collection, delegate, msg):
    collection[msg.id] = msg, delegate

def collect_with(collector):
    def dec(func):
        func.collector = collector
        return func
    return dec

@collect_with(atom_collect)
@defer.inlineCallbacks
def reply_delegate(msg):
    """
    ATOM!!!
    function to handle replies to pyhkals tweet
    """
    id = extract_id(msg.id)
    name = msg.title.split(':',1)[0]
    source = User(name)
    # wait for identity
    yield source.identity_deferred
    target = Reply(id)
    realmsg = msg.title.split(': ',1)[1]
    e = Tweet(target, source, realmsg, id)
    # create another event without @PyHKAL in msg.title
    e2 = Tweet(target, source, realmsg.split(' ',1)[1], id)
    dispatch_event('twitter.reply', e2)
    dispatch_event('twitter.mention', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e2)

    """ Scan msg or event.content for
    commands and dispatch if found
    """
    event = Tweet(target, source, realmsg.split(' ',2)[2], id)
    if event.content.strip():
        command = realmsg.split(' ',2)[1]
        dispatch_command(command, event)

@collect_with(xml_collect)
@defer.inlineCallbacks
def friend_delegate(msg):
    """
    function to handle our friends's tweets
    """
    source = User(msg.user.screen_name)
    # wait for identity
    yield source.identity_deferred
    target = Friend(msg.id)
    e = Tweet(target, source, unescape(msg.text), msg.id)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e)

@collect_with(xml_collect)
@defer.inlineCallbacks
def mention_delegate(msg):
    """
    function to handle tweets containing
    @PyHKAL (not necessarily as the first word)
    """
    source = User(msg.user.screen_name)
    # wait for identity
    yield source.identity_deferred
    target = Mention(msg.id)
    e = Tweet(target, source, unescape(msg.text), msg.id)
    dispatch_event('twitter.mention', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e)

@collect_with(xml_collect)
@defer.inlineCallbacks
def direct_delegate(msg):
    source = User(msg.sender.screen_name)
    # wait for identity
    yield source.identity_deferred
    target = Mention(msg.id)
    realmsg = unescape(msg.text)
    e = Tweet(target, source, realmsg, msg.id)
    dispatch_event('twitter.direct', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e)
    """ Scan msg or event.content for
    commands and dispatch if found
    """
    event = Tweet(target, source, realmsg.split(' ',1)[1], id)
    if event.content.strip():
        command = realmsg.split(' ',1)[0]
        dispatch_command(command, event)


@defer.inlineCallbacks
def refresh_task():
    global since_id
    collection = {}
    tw = twit()
    tasks = [
                (tw.friends, friend_delegate),
                (tw.mentions, mention_delegate),
                (tw.replies, reply_delegate),
                (tw.direct_messages, direct_delegate),
            ]
    for task, delegate in tasks:
        params = {'since_id':str(since_id)} \
                 if since_id > 0 else {}
        yield task(
                    partial(
                        delegate.collector,
                        collection,
                        delegate
                    ),
                    params=params
                  )

    for msg_id, (msg, delegate) in collection.iteritems():
        int_id = int(msg_id)
        if since_id < int_id:
            since_id = int_id
        delegate(msg)

    try:
        doc = yield davenport.openDoc('twitter')
    except:
        doc = {}
    doc['since_id'] = since_id
    davenport.saveDoc(doc, 'twitter')

#    return twit().replies(lambda x: reply_collect(collection, x), params={'since_id':str(since_id)}).addBoth(
#                lambda x: twit().friends(lambda x: friend_collect(collection,x), params={'since_id':str(since_id)}).addBoth(lambda x: refresh_done(collection))
#            )

refresher = LoopingCall(refresh_task)




# Initialization
@hook('startup')
@defer.inlineCallbacks
def startup():
    global since_id
    try:
        doc = yield davenport.openDoc('twitter')
        since_id = doc['since_id']
    except:
        pass

    refresher.start(REFRESHDELAY)


