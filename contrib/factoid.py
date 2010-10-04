import re
import random
import shlex

DEFAULT_PROBABILITY = 5

__settings__ = dict(
    factoidprobability="""Chance to trigger a factoid.""",
)

get_factoids = chaos("get_factoids", """
    if (doc.doctype == "factoid") {
        emit(doc.trigger, doc.reply);
    }
""")

factoids = {}
def cache(trigger, reply):
    factoids[re.compile(trigger, re.IGNORECASE | re.UNICODE)] = reply

@hook('startup')
@defer.inlineCallbacks
def start():
    global factoids
    docs = yield get_factoids()
    for doc in docs['rows']:
        cache(doc['key'], doc['value'])

@hook('message')
def trigger(event):
    p = remember('factoidprobability', DEFAULT_PROBABILITY)
    if random.random() * 100 <= p:
        matches = [reply for regexp, reply in factoids.iteritems()
                   if regexp.search(event.content)]
        if not matches:
            return
        match = random.choice(matches)
        event.reply(match)

@register('factoidadd')
def factoid_add(event):
    lexer = shlex.shlex(event.content)
    # set the quoting character to slash and retrieve the first word
    # thus ``/foo bar/ baz frob'' produces "foo bar" for its trigger
    lexer.quotes = '/'
    trigger = lexer.get_token()
    # retrieve all what's left of the payload
    reply = lexer.instream.read().lstrip()
    davenport.saveDoc(dict(doctype='factoid', trigger=trigger, reply=reply))
    cache(trigger, reply)
