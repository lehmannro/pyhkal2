"""

    Der fabuloese SpeedcubingMod

"""

import datetime #XXX consult event.time instead of datetime.time

__version__ = "0.2"

@hook("message", expr=r'^\*cube\b')
def startCubeTimer(event, r):
    if not hasattr(event.source, 'cube'):
        event.source.cube = datetime.datetime.now()

@hook("message")
def stopCubeTimer(event):
    if hasattr(event.source, 'cube'):
        if not event.content.startswith('*cube'):
            timed = datetime.datetime.now() - event.source.cube
            event.reply("%s: %s" % (event.source.nick, timed))
            del event.source.cube
