#!/usr/bin/env python

__version__ = "0.1"
__author__ = "crosbow"

SATZ = []
LASTAUTOR = ""
CONTRIBUTION = {}

"""
    TODO:
        - CouchDB
        - LOCK for concurrent adds
        - multiplier
        - save score
        - ???
"""


"""
#test object for debug
class Event():
    def __init__(self):
        self.content = "peter"
        self.source = Pser()

    def reply(self, w):
        print w

class Pser():
    def __init__(self):
        self.nick = "peter"
"""

@register("satz")
def processSatz(event):
    global LASTAUTOR
    word = event.content.split(" ")
    #print word
    if (word == ['']):
        if (SATZ == []):
            event.reply("Die letzten paar Woerter der Wortassoziationsgeschichte: <Erstes Wort vom neuen Satz ist gefragt! !Satz <Wort> zum hinschreiben.>")
        else:
            event.reply("Die letzten paar Woerter der Wortassoziationsgeschichte: %s" % (" ".join(SATZ[-11:])))
    elif (LASTAUTOR != event.source.nick):
        """
        komma syntax helper
         valid
            ", word" -> "last, word"
            "word,"
         invalid
            ",word" -> "last, word"
        """
        if (word[0] == ","):
            if (len(word) > 1):
                if (len(SATZ) > 0):
                    satzAppend(event, word[1], True)
        else:
            if (word[0][0] == ","):
                satzAppend(event, word[0][1:], True)
            else:
                satzAppend(event, word[0])
    else:
        event.reply("Noe. Du warst schon. :P")

@register("satzkill")
def satzKill(event):
    if (SATZ != []):
        if (LASTAUTOR == event.source.nick):
            CONTRIBUTION[event.source.nick] -= 1
            SATZ.pop()
            event.reply("\"%s\" aus dem aus dem aktuellen Wortassoziationssatz geloescht." % SATZ[len(SATZ)-1])
        else:
            event.reply("Dieses Wort kann nur %s loeschen!" % LASTAUTHOR)
    else:
        event.reply("Keine Worte vorhanden.")


def satzAppend(event, word, komma = False):
    global SATZ
    global LASTAUTOR
    global CONTRIBUTION
    LASTAUTOR = event.source.nick
    if (CONTRIBUTION.has_key(event.source.nick)):
        CONTRIBUTION[event.source.nick] += 1
    else:
        CONTRIBUTION[event.source.nick] = 1
    # komma syntax helper (also prevents ,,)
    if (komma):
        if (SATZ[len(SATZ)-1][-1:] != ","):
            SATZ[len(SATZ)-1] = SATZ[-1:][0]+","
    SATZ.append(word)
    if (word[-1:] in ".!?"):
        satzForge(event)

def satzForge(event):
    global SATZ
    global CONTRIBUTION
    event.reply(" ".join(SATZ))
    for x in CONTRIBUTION.items():
        event.reply("%s gab dem letzten Satz %i Woerter." % (x[0], x[1]))

    SATZ = []
    CONTRIBUTION = {}
    LASTAUTHOR = ""

"""
#test for debug
if __name__ == "__main__":
    event = Event()
    processSatz(event)
    event.content = ""
    event.source.nick ="o"
    processSatz(event)
    event.content = "neger,"
    event.source.nick ="peter"
    processSatz(event)
    event.content = ", nicht"
    event.source.nick ="p"
    processSatz(event)
    #satzKill(event)
    event.content = "toll."
    event.source.nick ="m"
    processSatz(event)
    print SATZ
"""
