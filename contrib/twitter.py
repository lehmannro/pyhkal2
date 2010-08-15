#!/usr/bin/env python
# coding: utf-8

from twittytwister.twitter import Twitter
from oauth import oauth
from functools import partial
from twisted.internet.task import LoopingCall


REFRESHDELAY = 60
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
    def __init__(self, name):
        Avatar.__init__(self)
        self.name = name
        self.identify()

    @defer.inlineCallbacks
    def identify(self):
        res = yield twitterIdentityView(key=self.name)
        if res['rows']:
            print res
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
    return twit().send_direct_message(msg, user=user, params=params)



def reply_delegate(msg):
    """
    ATOM!!!
    function to handle replies to pyhkals tweet
    """
    #print msg
    id = extract_id(msg.id)
    name = msg.title.split(':',1)[0]
    source = User(name)
    target = Reply(id)
    realmsg = msg.title.split(':',1)[1]
    e = Tweet(target, source, realmsg, id)
    # create another event without @PyHKAL in msg.title
    e2 = Tweet(target, source, realmsg.split(' ',2)[2], id)
    dispatch_event('twitter.reply', e2)
    dispatch_event('twitter.mention', e)
    dispatch_event('twitter.msg', e)
    dispatch_event('msg', e)

    def command_check(event):
        """ Scan msg or event.content for
        commands and dispatch if found
        """
        if event.content.strip():
            command = event.content.split(' ')[0]
            dispatch_command(command, event)

    command_check(e2)

def friend_delegate(msg):
    """
    function to handle our friends's tweets
    """
    source = User(msg.user.screen_name)
    target = Friend(msg.id)
    e = Tweet(target, source, unescape(msg.text), msg.id)
    dispatch_event('twitter.msg', e)
    dispatch_event('msg', e)

def mention_delegate(msg):
    """
    function to handle tweets containing
    @PyHKAL (not necessarily as the first word)
    """
    source = User(msg.user.screen_name)
    target = Mention(msg.id)
    e = Tweet(target, source, unescape(msg.text), msg.id)
    dispatch_event('twitter.msg', e)
    dispatch_event('twitter.mention', e)
    dispatch_event('msg', e)


# TODO change collect funtions to xml_collect 
# and atom_collect
def reply_collect(collection, msg):
    msg_id = extract_id(msg.id)
    collection[msg_id] = msg, reply_delegate

def friend_collect(collection, msg):
    collection[msg.id] = msg, friend_delegate

def mention_collect(collection, msg):
    collection[msg.id] = msg, mention_delegate

@defer.inlineCallbacks
def refresh_task():
    global since_id
    collection = {}
    params = {'since_id':str(since_id)}
    yield twit().friends(partial(friend_collect, collection), params=params)
    yield twit().mentions(partial(mention_collect, collection), params=params)
    yield twit().replies(partial(reply_collect, collection), params=params)

    for msg_id, (msg, delegate) in collection.iteritems():
        int_id = int(msg_id)
        if since_id < int_id:
            since_id = int_id
        delegate(msg)

#    return twit().replies(lambda x: reply_collect(collection, x), params={'since_id':str(since_id)}).addBoth(
#                lambda x: twit().friends(lambda x: friend_collect(collection,x), params={'since_id':str(since_id)}).addBoth(lambda x: refresh_done(collection))
#            )

refresher = LoopingCall(refresh_task)




# Initialization
@hook('startup')
def startup():
    refresher.start(REFRESHDELAY)


