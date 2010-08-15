#!/usr/bin/env python
#-*- coding:utf-8 -*-

__version__ = "0.1"
#__requires__ = ["irc"]

import datetime, time, re, functools

getKarma = chaos("getKarma","""
    if (doc.doctype == "karma") {
        emit(doc.name, doc.value);
    } 
    """
)

setKarma = chaos('setKarma',"")
karmaspam = 600

@defer.inlineCallbacks
def karma_edit(event, wort, delta):
    wort = wort.lower()
    result = yield getKarma(key=wort, include_docs='true')
    #print "DB antwort fuer getkarma key=", wort, 'ist' , result
    if result[u'rows']: # karma erhöhen
        entry = result[u'rows'][0][ u'doc'] #[u'id']
        #print "es gibt schon karma fuer", wort, entry
        if (time.time() - entry[u'updated_at']) > karmaspam:
            entry[u'value'] += delta
            entry[u'updated_at'] = time.time()      # printable wirds durch time.ctime(updated_at)
            event.reply("%s hat nun einen karmawert von %s" % (wort, entry[u'value']))
            #print "nun speicher ich das neue doch", entry
            yield davenport.saveDoc(entry) # entry in DB stecken
        else:
            rest = seconds2string(karmaspam - (time.time() - entry[u'updated_at']))
            event.reply("%s ist noch %s blockiert" % (wort, rest))
    else: # neuen adden
        #print "wir adden karma neu"
        entry = {u'doctype': 'karma', u'name': wort, u'value': delta, u'updated_at': time.time(), u'created_at': time.time() }
        event.reply("%s hat nun einen karmawert von %s" % (wort, delta))  
        yield davenport.saveDoc(entry) # entry in db stecken

@hook("message", r"\b(\w+)\+\+")
def karma_add(event, wort):
    return karma_edit(event, wort, +1)

@hook("message", r"\b(\w+)--")
def karma_del(event, wort):
    return karma_edit(event, wort, -1)
        
@hook("message", r"\b(\w+)==")
@defer.inlineCallbacks
def karma_say(event, wort):
    wort = wort.lower()
    result = yield getKarma(key=wort)
    if result[u'rows']: # karma erhöhen
        value = result[u'rows'][0][u'value']
    else:
        value = 0
    event.reply("%s hat einen karmawert von %s" % (wort, value))

def seconds2string(sec):
    return str(datetime.timedelta(seconds=sec))[2:]

