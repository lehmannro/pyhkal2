#!/usr/bin/env python
#-*- coding:utf-8 -*-

TIMEOUT = 600

__version__ = "0.1"
__author__ = "freddyb"
__settings__ = dict(
    karma=dict(
        timeout="""Number of seconds an item is blocked for karma modifications
            after a sucessful change. Defaults to %d.""" % TIMEOUT,
    )
)

import datetime, time, re
from twisted.web.error import Error

getKarma = chaos("getKarma","""
    if (doc.doctype == "karma") {
        emit(doc.name, doc.value);
    } 
    """
)

@defer.inlineCallbacks
def karma_edit(event, wort, delta):
    wort = wort.lower()

    # fetch old value, if any
    try:
        result = yield getKarma(key=wort, include_docs='true')
    except Error:
        result = dict(rows=0)

    # existing entry found;  update
    if result[u'rows']:
        # looking for the key ensures there is exactly *one* result row
        entry = result[u'rows'][0]['doc']

        karmaspam = remember("karma timeout", TIMEOUT)

        # Karma modifications MUST only occur at set intervals.  These are
        # purely game dynamics and do *not* facilitate any spam protection.
        if time.time() - entry[u'updated_at'] > karmaspam:
            entry[u'value'] += delta
            entry[u'updated_at'] = time.time()
            # Note: this is an update because the document carries its docid
            yield davenport.saveDoc(entry)
            # XXX I'm unsure if waiting for the database is really required
            #     here.  We should just continue.
            event.reply("%s hat nun einen karmawert von %s" % (wort, entry[u'value']))
        else:
            rest = seconds2string(karmaspam - (time.time() - entry[u'updated_at']))
            event.reply("%s ist noch %s blockiert" % (wort, rest))
    # item not found;  create new
    else:
        entry = dict(doctype='karma', name=wort, value=delta,
                     updated_at=time.time(), created_at=time.time())
        yield davenport.saveDoc(entry) # XXX same qualifier as above
        event.reply("%s hat nun einen karmawert von %s" % (wort, delta))

@hook("message", r"(\S\S+)\+\+(?:\s|$)")
def karma_add(event, wort):
    return karma_edit(event, wort, +1)

@hook("message", r"([\S]\S+)--(?:\s|$)")
def karma_del(event, wort):
    return karma_edit(event, wort, -1)

@hook("message", r"(\S\S+)==(?:\s|$)")
@defer.inlineCallbacks
def karma_say(event, wort):
    wort = wort.lower()
    try:
        result = yield getKarma(key=wort)
    except Error:
        result = dict(rows=0) # fall through the following if statement
    if result[u'rows']:
        value = result['rows'][0]['value']
    else:
        value = 0
    event.reply("%s hat einen karmawert von %s" % (wort, value))

def seconds2string(sec):
    return str(datetime.timedelta(seconds=sec))[2:]
