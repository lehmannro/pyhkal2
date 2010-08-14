#!/usr/bin/env python

from twittytwister import twitter
from oauth import oauth
from twisted.internet.task import LoopingCall

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
        return self.target.reply(msg)


class Reply(Location):
    def __init__(self, id):
        self.id = id

    def message(self, msg, params=None):
        return tweet(msg, params)

    def reply(self, msg):
        return self.message(
                    msg, 
                    params={'in_reply_to_status_id':self.id}
                )
    
class User(Avatar):
    def __init__(self, name):
        self.name = name
    def message(self, msg, params=None):
        return twit().send_direct_message(msg, self.name, params)
    def __eq__(self, obj):
        return isinstance(obj, User) and self.name.lower() == obj.name.lower()
    def __hash__(self):
        return hash(self.name.lower())
    
    
def twit():
    return twitter.Twitter(consumer=con, token=tok)

def tweet(msg, params=None):
    # FIXME UNICODE
    print msg
    msg = u'' + msg
    params = params or {}
    return twit().update(msg, params=params)

def tweet_direct(msg, user, params=None):
    params = params or {}
    return twit().send_direct_message(msg, user=user, params=params)


REFRESHDELAY = 60

def reply_delegate(msg):
    id = extract_id(msg.id)
    source = User(msg.author.name)
    target = Reply(id)
    e = Tweet(target, source, msg.title, id)
    dispatch_event('twitter.reply', e)
    dispatch_event('twitter.privmsg', e)
    dispatch_event('privmsg', e)

    if 'trigger' in msg.title:
        target.reply("YAY")

def refresh_task():
    return twit().replies(reply_delegate)

refresher = LoopingCall(refresh_task)


# Initialization
@hook('startup')
def startup():
    refresher.start(REFRESHDELAY)
    
    


#@hook('privmsg')
#def test(event):
#    tweet(event.content.split(' ', 1)[1]).addBoth(event.reply)




