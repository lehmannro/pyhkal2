import re
import random
import shlex

DEFAULT_PROBABILITY = 50

__settings__ = dict(
    factoidprobability="""Chance to trigger a factoid.""",
)

get_factoids = chaos("get_factoids", """
    if (doc.doctype == "factoid") {
        emit(doc.trigger, doc.reply);
    }
""")

factoids = {}
def cache(id_, trigger, reply):
    factoids[id_] = (re.compile(trigger, re.IGNORECASE | re.UNICODE), reply)

@hook('startup')
@defer.inlineCallbacks
def start():
    global factoids
    docs = yield get_factoids()
    for doc in docs['rows']:
        cache(doc['id'], doc['key'], doc['value'])

@hook('message')
def trigger(event):
    p = remember('factoidprobability', DEFAULT_PROBABILITY)
    if random.random() * 100 <= p:
        matches = [(regexp, reply) for regexp, reply in factoids.itervalues()
                   if regexp.search(event.content)]
        if not matches:
            return
        regexp, reply = random.choice(matches)
        match = regexp.sub(reply, regexp.search(event.content).group(0))
        match = match.replace('$who', event.source.name)
        if match.startswith("A:"):
            if hasattr(event.target, 'action'):
                event.target.action(match[2:])
            else:
                event.reply(match[2:])
        else:
            event.reply(match)

@register('factoidadd')
@defer.inlineCallbacks
def factoid_add(event):
    lexer = shlex.shlex(event.content)
    # set the quoting character to slash and retrieve the first word
    # thus ``/foo bar/ baz frob'' produces "foo bar" for its trigger
    lexer.quotes = '/'
    trigger = lexer.get_token()
    # retrieve all what's left of the payload
    reply = lexer.instream.read().lstrip()
    factoid = yield davenport.saveDoc(dict(doctype='factoid',
        trigger=trigger, reply=reply, creator=event.source.name))
    cache(factoid['id'], trigger, reply)
