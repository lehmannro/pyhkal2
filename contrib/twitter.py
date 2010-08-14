#!/usr/bin/env python

from twittytwister.twitter import Twitter
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
        return self.target.reply("@%s %s" % (self.source.name, msg))


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
    return Twitter(consumer=con, token=tok)

def tweet(msg, params=None):
    params = params or {}
    return twit().update(msg,  params=params)

def tweet_direct(msg, user, params=None):
    params = params or {}
    return twit().send_direct_message(msg, user=user, params=params)


REFRESHDELAY = 60

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
    dispatch_event('twitter.privmsg', e)
    dispatch_event('privmsg', e)

    def command_check(event):
        """ Scan msg or event.content for
        commands and dispatch if found
        """
        if event.content.strip():
            command = event.content.split(' ')[0]
            dispatch_command(command, event)
    
    command_check(e2)



def refresh_task():
    return twit().replies(reply_delegate)

refresher = LoopingCall(refresh_task)




# Initialization
@hook('startup')
def startup():
    refresher.start(REFRESHDELAY)
    

