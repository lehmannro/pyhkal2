#!/usr/bin/env python
# coding: utf-8

from twittytwister.twitter import Twitter
from oauth import oauth
from functools import partial
from twisted.internet.task import LoopingCall
from datetime import datetime


REFRESHDELAY = remember("twitter refresh", 60)
WRITE_SINCE_ID = remember("twitter write_since_id", True)

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


class TweetEvent(Event):
    def __init__(self, target, source, content, id, timestamp):
        Event.__init__(self, target, source, content, timestamp)
        self.id = id
    def reply(self, msg):
        return self.target.reply("@%s %s" % (self.source.name, msg))


class Tweet(Location):
    def __init__(self, id):
        Location.__init__(self)
        self.id = id

class PublicTweet(Tweet):
    def message(self, msg, params=None):
        return tweet(msg, params)

    def reply(self, msg):
        return self.message(
                    msg,
                    params={'in_reply_to_status_id':self.id}
                )
    def retweet(self):
        return retweet(self.id)

class PrivateTweet(Tweet):
    def __init__(self, id, sender):
        self.id = id
        self.sender = sender
    def message(self, msg, params=None):
        return direct_message(msg, self.sender, params)
    def reply(self, msg):
        return self.message(msg)

class Reply(PublicTweet):
    pass

class Friend(PublicTweet):
    pass

class Mention(PublicTweet):
    pass


class Direct(PrivateTweet):
    pass

class User(Avatar):
    __metaclass__ = MultitonMeta
    users = set()
    def __init__(self, name):
        Avatar.__init__(self, name)
        self.name = name
        self.identity_deferred = self.identify()
        self.users.add(self)

    @defer.inlineCallbacks
    def identify(self):
        res = yield twitterIdentityView(key=self.name)
        if res['rows']:
            identity = Identity(res['rows'][0]['id'])
            identity.link(self)

    def message(self, msg, params=None):
        return direct_message(msg, self.name, params)
    def __eq__(self, obj):
        return isinstance(obj, User) and self.name.lower() == obj.name.lower()
    def __hash__(self):
        return hash(self.name.lower())


def twit():
    return Twitter(consumer=con, token=tok)

def tweet(msg, params=None):
    params = params or {}
    return twit().update(msg,  params=params)

def retweet(id, delegate=lambda x: 0):
    return twit().retweet(id, delegate)

def direct_message(msg, user, params=None):
    params = params or {}
    return twit().send_direct_message(msg, screen_name=user, params=params)

def follow(user):
    return twit().follow(user)

def leave(user):
    return twit().leave(user)

def block(user):
    return twit().block(user)



def xml_date(entry):
    """Example:
    Thu Jul 15 23:24:33 +0000 2010"""
    return datetime.strptime(
                entry.created_at, 
                '%a %b %d %H:%M:%S +0000 %Y'
            )
def atom_date(entry):
    """Example:
    2010-08-25T15:53:19+00:00"""
    return datetime.strptime(
                entry.published,
                '%Y-%m-%dT%H:%M:%S+00:00'
            )


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
    e = TweetEvent(target=target, source=source, content=realmsg, id=id, timestamp=atom_date(msg))
    # create another event without @PyHKAL in msg.title
    e2 = TweetEvent(target=target, source=source, content=realmsg.split(' ',1)[1], id=id, timestamp=atom_date(msg))
    dispatch_event('twitter.reply', e2)
    dispatch_event('twitter.mention', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e2)

    """ Scan msg or event.content for
    commands and dispatch if found
    """
    if len(realmsg.split(' ')) > 2:
        event = TweetEvent(target=target, source=source, content=realmsg.split(' ',2)[2], id=id, timestamp=atom_date(msg))
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
    e = TweetEvent(target=target, source=source, content=unescape(msg.text), id=msg.id, timestamp=xml_date(msg))
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
    e = TweetEvent(target=target, source=source, content=unescape(msg.text), id=msg.id, timestamp=xml_date(msg))
    dispatch_event('twitter.mention', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e)

@collect_with(xml_collect)
@defer.inlineCallbacks
def direct_delegate(msg):
    source = User(msg.sender.screen_name)
    # wait for identity
    yield source.identity_deferred
    target = Direct(msg.id, source.name)
    realmsg = unescape(msg.text)
    e = TweetEvent(target=target, source=source, content=realmsg, id=msg.id, timestamp=xml_date(msg))
    dispatch_event('twitter.direct', e)
    dispatch_event('twitter.message', e)
    dispatch_event('message', e)
    """ Scan msg or event.content for
    commands and dispatch if found
    """
    if len(realmsg.split(' ')) > 1:
        event = TweetEvent(target=target, source=source, content=realmsg.split(' ',1)[1], id=id, timestamp=xml_date(msg))
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

    if WRITE_SINCE_ID:
        try:
            doc = yield davenport.openDoc('twitter')
        except:
            doc = {}
        doc['since_id'] = since_id
        davenport.saveDoc(doc, 'twitter')

#    return twit().replies(lambda x: reply_collect(collection, x), params={'since_id':str(since_id)}).addBoth(
#                lambda x: twit().friends(lambda x: friend_collect(collection,x), params={'since_id':str(since_id)}).addBoth(lambda x: refresh_done(collection))
#            )



def loop(*args):
    refresher = LoopingCall(refresh_task)
    refresher.start(REFRESHDELAY).addBoth(loop)

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
    
    loop()


